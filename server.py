"""
BRHS Chatbot – FastAPI backend
Serves the embeddable chat widget and a /api/chat endpoint.

Usage:
    python server.py
Then embed on any page with:
    <script src="http://localhost:8000/static/embed.js"></script>
"""

import os
import json
import hashlib
import numpy as np
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
import anthropic
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from dotenv import load_dotenv

def _load_env():
    """Load .env from the same directory as this file, trying multiple path resolutions."""
    candidates = [
        os.path.join(os.path.dirname(os.path.abspath(__file__)), ".env"),
        os.path.join(os.getcwd(), ".env"),
        r"C:\Users\suraj\brhs-chatbot\.env",
    ]
    for path in candidates:
        if os.path.exists(path):
            with open(path, encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith("#") and "=" in line:
                        k, _, v = line.partition("=")
                        os.environ[k.strip()] = v.strip()
            return
_load_env()

KB_FILE    = "knowledge_base.json"
CACHE_FILE = "response_cache.json"
TOP_K      = 6
MAX_CONTEXT_CHARS = 12000
MODEL      = "claude-haiku-4-5"

SYSTEM_PROMPT = """You are a helpful, knowledgeable assistant for Bridgewater-Raritan High School (BRHS) located in Bridgewater, NJ.

You answer questions using information scraped from the official school website (hs.brrsd.org), including web pages and PDF documents such as course catalogs, scheduling guides, and counseling resources.

Guidelines:
- Base your answers on the provided context excerpts from the school website.
- If the context doesn't contain the information needed, say so clearly and suggest the user visit hs.brrsd.org directly or contact the school.
- When citing specific information, mention the source page or document.
- Be friendly, accurate, and concise.
- For course registration, scheduling, and counseling information, provide detailed, actionable answers.
- Do not invent information not present in the context."""


# ── Load knowledge base once at startup ──────────────────────────────────────

def _load_kb():
    if not os.path.exists(KB_FILE):
        return None, None
    with open(KB_FILE, "r", encoding="utf-8") as f:
        kb = json.load(f)
    if not kb:
        return None, None
    texts = [item["content"] for item in kb]
    vectorizer = TfidfVectorizer(
        max_features=20000, ngram_range=(1, 2),
        stop_words="english", sublinear_tf=True
    )
    matrix = vectorizer.fit_transform(texts)
    return kb, (vectorizer, matrix)

KB, INDEX = _load_kb()


def search(query: str, top_k: int = TOP_K) -> list[dict]:
    if KB is None or INDEX is None:
        return []
    vectorizer, matrix = INDEX
    q_vec = vectorizer.transform([query])
    sims  = cosine_similarity(q_vec, matrix)[0]
    top_idx = np.argsort(sims)[::-1][:top_k * 3]
    seen_urls, results = set(), []
    for idx in top_idx:
        if sims[idx] < 0.02:
            break
        item = KB[idx]
        url_count = sum(1 for r in results if r["url"] == item["url"])
        if url_count >= 2:
            continue
        results.append({**item, "score": float(sims[idx])})
        if len(results) >= top_k:
            break
    return results


def build_context(chunks: list[dict]) -> str:
    parts, total = [], 0
    for c in chunks:
        header = f"[{c['type'].upper()}] {c['title']}\nURL: {c['url']}"
        block  = f"{header}\n\n{c['content']}"
        if total + len(block) > MAX_CONTEXT_CHARS:
            break
        parts.append(block)
        total += len(block)
    return "\n\n" + ("─" * 60) + "\n\n".join(parts)


# ── Cache helpers ─────────────────────────────────────────────────────────────

def _load_cache() -> dict:
    if os.path.exists(CACHE_FILE):
        try:
            with open(CACHE_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    return {}

def _save_cache(cache: dict) -> None:
    with open(CACHE_FILE, "w", encoding="utf-8") as f:
        json.dump(cache, f, indent=2, ensure_ascii=False)

def cache_key(question: str) -> str:
    return hashlib.md5(question.strip().lower().encode()).hexdigest()


# ── FastAPI app ───────────────────────────────────────────────────────────────

app = FastAPI(title="BRHS Chatbot")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://hs.brrsd.org", "http://localhost:8000"],
    allow_methods=["*"],
    allow_headers=["*"],
)


class ChatRequest(BaseModel):
    message: str
    history: list[dict] = []   # [{role, content}, …]


@app.post("/api/chat")
async def chat(req: ChatRequest):
    api_key = os.environ.get("ANTHROPIC_API_KEY", "")
    if not api_key:
        def _err():
            yield f"data: {json.dumps({'error': 'Server is missing ANTHROPIC_API_KEY.'})}\n\n"
            yield f"data: {json.dumps({'done': True, 'sources': []})}\n\n"
        return StreamingResponse(_err(), media_type="text/event-stream")

    # Retrieve context
    relevant = search(req.message)
    context  = build_context(relevant)

    cache = _load_cache()
    ck    = cache_key(req.message)

    def stream_response():
        # ── Cache hit: replay as SSE so the client always sees a stream ───────
        if ck in cache and not req.history:
            cached  = cache[ck]
            reply   = cached.get("response", "")
            sources = cached.get("sources", [])
            yield f"data: {json.dumps({'delta': reply})}\n\n"
            yield f"data: {json.dumps({'done': True, 'sources': sources, 'cached': True})}\n\n"
            return

        # ── Build message list for Claude ─────────────────────────────────────
        history_turns = []
        for m in req.history[-12:]:
            history_turns.append({"role": m["role"], "content": m["content"]})

        history_turns.append({
            "role": "user",
            "content": (
                f"Here is relevant information from the BRHS website:\n{context}\n\n"
                f"---\n\nUser question: {req.message}"
            ),
        })

        client_ai = anthropic.Anthropic(api_key=api_key)
        full = ""
        try:
            with client_ai.messages.stream(
                model=MODEL,
                max_tokens=1024,
                system=SYSTEM_PROMPT,
                messages=history_turns,
            ) as stream:
                for chunk in stream.text_stream:
                    full += chunk
                    yield f"data: {json.dumps({'delta': chunk})}\n\n"
        except Exception as e:
            yield f"data: {json.dumps({'error': str(e)})}\n\n"
            return

        # Deduplicate sources
        seen, deduped = set(), []
        for s in relevant:
            if s["url"] not in seen:
                deduped.append({"title": s["title"], "url": s["url"], "type": s["type"]})
                seen.add(s["url"])

        # Persist to cache
        cache[ck] = {"response": full, "sources": deduped}
        _save_cache(cache)

        yield f"data: {json.dumps({'done': True, 'sources': deduped})}\n\n"

    return StreamingResponse(stream_response(), media_type="text/event-stream")


# ── Serve static widget files ─────────────────────────────────────────────────

app.mount("/static", StaticFiles(directory="static"), name="static")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)
