"""
BRHS Website Scraper
Crawls https://hs.brrsd.org/ and all sublinks, extracts text content and PDFs,
saves everything to knowledge_base.json for use by the chatbot.

Usage:
    python scraper.py
"""

import requests
from bs4 import BeautifulSoup
from playwright.sync_api import sync_playwright
import pdfplumber
import json
import re
import io
import os
import time
from urllib.parse import urljoin, urlparse
from collections import deque

BASE_URL = "https://hs.brrsd.org"
OUTPUT_FILE = "knowledge_base.json"
MAX_PAGES = 1000       # Max HTML pages to crawl
CHUNK_SIZE = 1200      # Characters per chunk
CHUNK_OVERLAP = 150    # Overlap between chunks
PAGE_TIMEOUT = 30000   # ms to wait for page load
WAIT_AFTER_LOAD = 2000 # ms to wait after domcontentloaded for JS to render

SKIP_EXTENSIONS = {
    '.jpg', '.jpeg', '.png', '.gif', '.svg', '.ico',
    '.css', '.js', '.mp4', '.mp3', '.wav', '.zip',
    '.doc', '.docx', '.xls', '.xlsx', '.ppt', '.pptx',
    '.woff', '.woff2', '.ttf', '.eot'
}

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    ),
}


def is_same_domain(url: str) -> bool:
    parsed = urlparse(url)
    return parsed.netloc in ("hs.brrsd.org", "www.hs.brrsd.org", "")


def should_skip_url(url: str) -> bool:
    lower = url.lower()
    parsed = urlparse(lower)
    ext = os.path.splitext(parsed.path)[1]
    if ext in SKIP_EXTENSIONS:
        return True
    skip_patterns = ["facebook.com", "twitter.com", "instagram.com", "youtube.com",
                     "login", "logout", "sign-in", "register", "calendar?"]
    return any(p in lower for p in skip_patterns)


def normalize_url(url: str) -> str:
    """Remove fragments and trailing slashes for dedup."""
    url = url.split('#')[0].rstrip('/')
    return url


def extract_pdf_text(content: bytes) -> str:
    """Extract full text from a PDF byte string."""
    try:
        with pdfplumber.open(io.BytesIO(content)) as pdf:
            pages = []
            for page in pdf.pages:
                text = page.extract_text()
                if text:
                    pages.append(text.strip())
            return "\n\n".join(pages)
    except Exception as e:
        print(f"    PDF error: {e}")
        return ""


def extract_html_text(html: str) -> tuple:
    """Return (title, main_text) from rendered HTML string."""
    soup = BeautifulSoup(html, 'lxml')

    title_tag = soup.find('title')
    title = title_tag.get_text(strip=True) if title_tag else ""

    for tag in soup.find_all(['script', 'style', 'noscript', 'iframe',
                               'nav', 'footer', 'header', 'aside',
                               'form', 'button']):
        tag.decompose()

    main = (
        soup.find('main')
        or soup.find(id=re.compile(r'^(content|main)$', re.I))
        or soup.find(class_=re.compile(r'(^|\s)(main-content|page-content|article-body)(\s|$)', re.I))
        or soup.find('article')
        or soup.body
    )
    if main is None:
        main = soup

    raw = main.get_text(separator=' ', strip=True)
    text = re.sub(r'\s{2,}', ' ', raw).strip()
    return title, text


def chunk_text(text: str, source_url: str, title: str, doc_type: str) -> list:
    """Split text into overlapping chunks with metadata."""
    if not text or len(text) < 80:
        return []

    chunks = []
    start = 0
    while start < len(text):
        end = min(start + CHUNK_SIZE, len(text))
        chunk = text[start:end]

        if end < len(text):
            for sep in ('. ', '! ', '? ', '\n'):
                pos = chunk.rfind(sep, int(CHUNK_SIZE * 0.6))
                if pos != -1:
                    chunk = chunk[:pos + len(sep)]
                    end = start + pos + len(sep)
                    break

        if chunk.strip():
            chunks.append({
                "url": source_url,
                "type": doc_type,
                "title": title,
                "content": chunk.strip()
            })

        if end >= len(text):
            break
        start = end - CHUNK_OVERLAP

    return chunks


def fetch_pdf(url: str) -> bytes:
    """Fetch a PDF via requests (no JS needed)."""
    resp = requests.get(url, headers=HEADERS, timeout=20)
    resp.raise_for_status()
    return resp.content


def scrape():
    visited: set = set()
    queue: deque = deque([BASE_URL])
    knowledge_base: list = []
    pdf_urls: set = set()
    html_count = 0

    print(f"Starting crawl of {BASE_URL}")
    print(f"Max pages: {MAX_PAGES}  |  Chunk size: {CHUNK_SIZE} chars\n")

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(
            user_agent=HEADERS["User-Agent"],
            ignore_https_errors=True,
        )
        page = context.new_page()

        while queue and html_count < MAX_PAGES:
            url = normalize_url(queue.popleft())

            if url in visited or should_skip_url(url):
                continue
            visited.add(url)

            is_pdf = url.lower().endswith('.pdf')

            try:
                # PDFs: fetch with requests, no browser needed
                if is_pdf:
                    if url in pdf_urls:
                        continue
                    pdf_urls.add(url)
                    print(f"  [PDF] {url}")
                    content = fetch_pdf(url)
                    pdf_name = url.split('/')[-1].replace('-', ' ').replace('_', ' ')
                    pdf_name = re.sub(r'\.\w+$', '', pdf_name).strip() or "Document"
                    text = extract_pdf_text(content)
                    if text:
                        chunks = chunk_text(text, url, pdf_name, "pdf")
                        knowledge_base.extend(chunks)
                        print(f"         -> {len(chunks)} chunks from '{pdf_name}'")
                    continue

                # HTML pages: use Playwright for JS rendering
                response = page.goto(url, wait_until="domcontentloaded", timeout=PAGE_TIMEOUT)
                if response is None:
                    continue

                final_url = normalize_url(page.url)
                content_type = response.headers.get('content-type', '').lower()

                # Redirect landed on a PDF
                if 'pdf' in content_type or final_url.lower().endswith('.pdf'):
                    if final_url not in pdf_urls:
                        pdf_urls.add(final_url)
                        print(f"  [PDF] {final_url}")
                        content = fetch_pdf(final_url)
                        pdf_name = final_url.split('/')[-1].replace('-', ' ').replace('_', ' ')
                        pdf_name = re.sub(r'\.\w+$', '', pdf_name).strip() or "Document"
                        text = extract_pdf_text(content)
                        if text:
                            chunks = chunk_text(text, final_url, pdf_name, "pdf")
                            knowledge_base.extend(chunks)
                            print(f"         -> {len(chunks)} chunks from '{pdf_name}'")
                    continue

                if 'html' not in content_type:
                    continue

                # Wait a bit extra for dynamic content to settle
                page.wait_for_timeout(WAIT_AFTER_LOAD)

                html_count += 1
                rendered_html = page.content()
                title, text = extract_html_text(rendered_html)

                status = f"[{html_count}] {final_url[:90]}"
                if text and len(text) > 80:
                    chunks = chunk_text(text, final_url, title or final_url, "html")
                    knowledge_base.extend(chunks)
                    status += f"  -> {len(chunks)} chunks"
                print(status)

                # Discover new links from the rendered DOM
                links = page.eval_on_selector_all(
                    'a[href]',
                    'els => els.map(e => e.href)'
                )
                for href in links:
                    href = href.strip()
                    if not href or href.startswith('mailto:') or href.startswith('tel:') or href.startswith('javascript:'):
                        continue
                    full = normalize_url(href)
                    if is_same_domain(full) and full not in visited:
                        queue.append(full)

            except Exception as e:
                print(f"  ERROR [{url}]: {e}")

        browser.close()

    return knowledge_base


def save(knowledge_base: list) -> None:
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        json.dump(knowledge_base, f, indent=2, ensure_ascii=False)


if __name__ == "__main__":
    kb = scrape()
    save(kb)
    print(f"\n{'='*60}")
    print(f"Scraped {len(kb)} content chunks")
    html_c = sum(1 for x in kb if x['type'] == 'html')
    pdf_c  = sum(1 for x in kb if x['type'] == 'pdf')
    print(f"  HTML chunks : {html_c}")
    print(f"  PDF  chunks : {pdf_c}")
    print(f"Saved -> {OUTPUT_FILE}")
