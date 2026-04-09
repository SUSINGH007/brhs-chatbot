"""
BRHS School Chatbot
Streamlit web app that uses Claude + the scraped knowledge base to answer
questions about Bridgewater-Raritan High School.

Usage:
    streamlit run app.py
"""

import os
import json
import hashlib
import numpy as np
import streamlit as st
import anthropic
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from dotenv import load_dotenv

load_dotenv()

KB_FILE = "knowledge_base.json"
CACHE_FILE = "response_cache.json"
TOP_K = 6               # Number of chunks to retrieve
MAX_CONTEXT_CHARS = 12000  # Rough cap to keep prompt reasonable
MODEL = "claude-haiku-4-5"

SYSTEM_PROMPT = """You are a helpful, knowledgeable assistant for Bridgewater-Raritan High School (BRHS) located in Bridgewater, NJ.

You answer questions using information scraped from the official school website (hs.brrsd.org), including web pages and PDF documents such as course catalogs, scheduling guides, and counseling resources.

Guidelines:
- Base your answers on the provided context excerpts from the school website.
- If the context doesn't contain the information needed, say so clearly and suggest the user visit hs.brrsd.org directly or contact the school.
- When citing specific information, mention the source page or document.
- Be friendly, accurate, and concise.
- For course registration, scheduling, and counseling information, provide detailed, actionable answers.
- Do not invent information not present in the context."""


# ── Response cache ────────────────────────────────────────────────────────────

def cache_key(question: str) -> str:
    """Normalize question and return an MD5 hash as cache key."""
    normalized = question.strip().lower()
    return hashlib.md5(normalized.encode()).hexdigest()

@st.cache_resource
def load_cache() -> dict:
    """Load persistent cache from disk (shared across all sessions)."""
    if os.path.exists(CACHE_FILE):
        try:
            with open(CACHE_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception:
            pass
    return {}

def save_cache(cache: dict) -> None:
    with open(CACHE_FILE, 'w', encoding='utf-8') as f:
        json.dump(cache, f, indent=2, ensure_ascii=False)


# ── Knowledge base loading & indexing ────────────────────────────────────────

@st.cache_resource(show_spinner="Loading knowledge base…")
def load_knowledge_base():
    if not os.path.exists(KB_FILE):
        return None, None

    with open(KB_FILE, 'r', encoding='utf-8') as f:
        kb = json.load(f)

    if not kb:
        return None, None

    texts = [item['content'] for item in kb]
    vectorizer = TfidfVectorizer(
        max_features=20000,
        ngram_range=(1, 2),
        stop_words='english',
        sublinear_tf=True
    )
    matrix = vectorizer.fit_transform(texts)
    return kb, (vectorizer, matrix)


def search(query: str, kb: list, index: tuple, top_k: int = TOP_K) -> list[dict]:
    vectorizer, matrix = index
    q_vec = vectorizer.transform([query])
    sims = cosine_similarity(q_vec, matrix)[0]
    top_idx = np.argsort(sims)[::-1][:top_k * 3]  # over-fetch, then de-dup by URL

    seen_urls = set()
    results = []
    for idx in top_idx:
        if sims[idx] < 0.02:
            break
        item = kb[idx]
        url = item['url']
        # Allow up to 2 chunks per URL to avoid one doc dominating
        url_count = sum(1 for r in results if r['url'] == url)
        if url_count >= 2:
            continue
        results.append({**item, "score": float(sims[idx])})
        if len(results) >= top_k:
            break

    return results


def build_context(chunks: list[dict]) -> str:
    parts = []
    total = 0
    for c in chunks:
        header = f"[{c['type'].upper()}] {c['title']}\nURL: {c['url']}"
        block = f"{header}\n\n{c['content']}"
        if total + len(block) > MAX_CONTEXT_CHARS:
            break
        parts.append(block)
        total += len(block)
    return "\n\n" + ("─" * 60) + "\n\n".join(parts)


# ── Streamlit UI ──────────────────────────────────────────────────────────────

st.set_page_config(
    page_title="BRHS School Assistant",
    page_icon="🏫",
    layout="wide",
)

# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.image("https://hs.brrsd.org/favicon.ico", width=40)
    st.title("BRHS Assistant")
    st.markdown("**Bridgewater-Raritan High School**")
    st.markdown("Ask about courses, scheduling, counseling, activities, and more.")
    st.divider()

    api_key = os.environ.get("ANTHROPIC_API_KEY", "")
    if not api_key:
        api_key = st.text_input("Anthropic API Key", type="password",
                                placeholder="sk-ant-…",
                                help="Get yours at console.anthropic.com")

    st.divider()
    st.caption("Powered by Claude & hs.brrsd.org")
    cache = load_cache()
    st.caption(f"🗂️ {len(cache)} cached answers")

# ── API key check ─────────────────────────────────────────────────────────────
if not api_key:
    st.info("Enter your Anthropic API key in the sidebar to start chatting.", icon="🔑")
    st.stop()

client = anthropic.Anthropic(api_key=api_key)

# ── Knowledge base check ──────────────────────────────────────────────────────
kb, index = load_knowledge_base()

if kb is None:
    st.error(
        "**Knowledge base not found.**\n\n"
        "Run the scraper first to build the knowledge base:\n"
        "```\npython scraper.py\n```",
        icon="⚠️"
    )
    st.stop()

with st.sidebar:
    html_count = sum(1 for x in kb if x['type'] == 'html')
    pdf_count  = sum(1 for x in kb if x['type'] == 'pdf')
    st.success(f"✓ {len(kb)} chunks loaded")
    st.caption(f"Web pages: {html_count} · PDFs: {pdf_count}")

# ── Main chat area ────────────────────────────────────────────────────────────
st.title("🏫 Bridgewater-Raritan High School Assistant")
st.caption("Ask me anything about BRHS – courses, scheduling, counseling, events, and more!")

# Session state
if "messages" not in st.session_state:
    st.session_state.messages = []
if "sources" not in st.session_state:
    st.session_state.sources = {}   # turn_index → list of source dicts

# Render history
for i, msg in enumerate(st.session_state.messages):
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])
        if msg["role"] == "assistant" and i in st.session_state.sources:
            srcs = st.session_state.sources[i]
            if srcs:
                with st.expander("📚 Sources used"):
                    shown = set()
                    for s in srcs:
                        if s['url'] not in shown:
                            st.markdown(f"- [{s['title']}]({s['url']}) `{s['type'].upper()}`")
                            shown.add(s['url'])

# Chat input
if prompt := st.chat_input("Ask a question about BRHS…"):

    # Add user message
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Retrieve relevant chunks
    relevant = search(prompt, kb, index)
    context = build_context(relevant)

    # Check cache first (only for single-turn questions, not mid-conversation)
    cache = load_cache()
    ck = cache_key(prompt)
    is_cached = ck in cache and len(st.session_state.messages) <= 1

    # Build messages for Claude (keep last 6 turns for context)
    history_turns = []
    for m in st.session_state.messages[-12:]:   # last 6 pairs
        role = m["role"]
        content = m["content"]
        # For the latest user turn, inject retrieved context
        if m is st.session_state.messages[-1]:  # current user message
            content = (
                f"Here is relevant information from the BRHS website:\n{context}\n\n"
                f"---\n\nUser question: {prompt}"
            )
        history_turns.append({"role": role, "content": content})

    # Stream Claude response
    with st.chat_message("assistant"):
        response_placeholder = st.empty()
        full_response = ""

        with st.spinner(""):
            try:
                if is_cached:
                    # Serve from cache — no API call
                    full_response = cache[ck]["response"]
                    relevant = cache[ck].get("sources", relevant)
                    response_placeholder.markdown(full_response)
                    st.caption("⚡ Served from cache")
                else:
                    with client.messages.stream(
                        model=MODEL,
                        max_tokens=1024,
                        system=SYSTEM_PROMPT,
                        messages=history_turns,
                    ) as stream:
                        for text_chunk in stream.text_stream:
                            full_response += text_chunk
                            response_placeholder.markdown(full_response + "▌")

                    response_placeholder.markdown(full_response)

                    # Save to cache
                    cache[ck] = {"response": full_response, "sources": relevant}
                    save_cache(cache)

                # Show sources
                turn_idx = len(st.session_state.messages)  # index BEFORE appending
                st.session_state.sources[turn_idx] = relevant
                if relevant:
                    with st.expander("📚 Sources used"):
                        shown = set()
                        for s in relevant:
                            if s['url'] not in shown:
                                st.markdown(f"- [{s['title']}]({s['url']}) `{s['type'].upper()}`")
                                shown.add(s['url'])

            except anthropic.AuthenticationError:
                full_response = "Invalid API key. Please check the key in the sidebar."
                response_placeholder.error(full_response)
            except anthropic.RateLimitError:
                full_response = "Rate limit reached. Please wait a moment and try again."
                response_placeholder.warning(full_response)
            except Exception as e:
                full_response = f"An error occurred: {e}"
                response_placeholder.error(full_response)

    st.session_state.messages.append({"role": "assistant", "content": full_response})
