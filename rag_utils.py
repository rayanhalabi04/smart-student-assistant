from typing import List, Tuple
import re
from collections import Counter
from datetime import datetime, timedelta, date

import numpy as np
from pypdf import PdfReader
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


# ----------------- Dummy Gemini setup (UI still calls this) ----------------- #

def set_gemini_api_key(api_key: str):
    """
    Kept only so app.py import doesn't break.
    We are running in OFFLINE mode, so this does nothing.
    """
    return


# ----------------- PDF → TEXT → CHUNKS ----------------- #

def extract_text_from_pdf(path: str) -> str:
    reader = PdfReader(path)
    pages = []
    for page in reader.pages:
        try:
            txt = page.extract_text() or ""
        except Exception:
            txt = ""
        pages.append(txt)
    return "\n\n".join(pages)


def split_into_chunks(text: str, chunk_size: int = 800, overlap: int = 200) -> List[str]:
    """
    Simple word-based chunking with overlap.
    """
    words = text.split()
    if not words:
        return []

    chunks: List[str] = []
    start = 0
    n = len(words)

    while start < n:
        end = min(start + chunk_size, n)
        chunk = " ".join(words[start:end])
        chunks.append(chunk)
        if end == n:
            break
        start = max(0, end - overlap)

    return chunks


# ----------------- TF-IDF STORE ----------------- #

class TfidfStore:
    def __init__(self, chunks: List[str]):
        self.chunks = chunks
        self.vectorizer = TfidfVectorizer(stop_words="english")
        self.matrix = self.vectorizer.fit_transform(chunks)

    def similarity_search(self, query: str, k: int = 5) -> List[Tuple[str, float]]:
        q_vec = self.vectorizer.transform([query])
        sims = cosine_similarity(q_vec, self.matrix)[0]
        idxs = np.argsort(-sims)[:k]
        return [(self.chunks[i], float(sims[i])) for i in idxs]


def build_store_from_pdf(path: str) -> TfidfStore:
    text = extract_text_from_pdf(path)
    chunks = split_into_chunks(text)
    if not chunks:
        raise ValueError("No text could be extracted from the PDF.")
    store = TfidfStore(chunks)
    store.raw_text = text
    return store


# ----------------- Helper: simple keyword extractor ----------------- #

def _extract_keywords(text: str, max_words: int = 40) -> List[str]:
    tokens = re.findall(r"[A-Za-z]{4,}", text.lower())
    if not tokens:
        return []
    counts = Counter(tokens)
    # skip super common boring words
    stop = {"this", "that", "these", "those", "have", "been", "which",
            "there", "where", "from", "with", "about", "other", "because"}
    keywords = [w for w, _ in counts.most_common() if w not in stop]
    return keywords[:max_words]


def _first_sentences(text: str, max_chars: int = 1200) -> str:
    sentences = re.split(r"(?<=[.!?])\s+", text.strip())
    out = []
    total = 0
    for s in sentences:
        if not s:
            continue
        if total + len(s) > max_chars and out:
            break
        out.append(s)
        total += len(s)
    return " ".join(out)


# ----------------- OFFLINE “AI” FUNCTIONS ----------------- #

def answer_question(question: str, store: TfidfStore) -> str:
    """
    Offline mode:
    - retrieve top chunks
    - show them as the answer + small explanation.
    """
    docs = store.similarity_search(question, k=3)
    if not docs:
        return "I couldn't find anything in the slides related to your question."

    parts = []
    for i, (chunk, score) in enumerate(docs, start=1):
        snippet = _first_sentences(chunk, max_chars=400)
        parts.append(f"{i}. {snippet}")

    joined = "\n\n".join(parts)

    return (
        "🔍 *Offline demo answer*\n\n"
        "Here are the most relevant notes from your slides for this question:\n\n"
        f"{joined}"
    )


def summarize_lecture(store: TfidfStore, detail: str = "medium") -> str:
    """
    Offline summary = take important sentences from the raw text.
    """
    base = _first_sentences(store.raw_text, max_chars={
        "short": 800,
        "medium": 1500,
        "long": 2500,
    }.get(detail, 1500))

    bullets = re.split(r"(?<=[.!?])\s+", base)
    bullets = [b.strip() for b in bullets if b.strip()]

    lines = [f"- {b}" for b in bullets]

    return (
        "📝 *Offline summary generated from your slides (no external LLM used).* \n\n"
        + "\n".join(lines)
    )


def generate_quiz(store: TfidfStore, num_questions: int = 8, difficulty: str = "medium") -> str:
    """
    Offline quiz:
    - use frequent keywords as topics for open questions.
    """
    keywords = _extract_keywords(store.raw_text, max_words=max(num_questions * 2, 10))
    if not keywords:
        return "Could not generate a quiz because not enough text/keywords were found."

    questions = []
    for i in range(num_questions):
        if i < len(keywords):
            kw = keywords[i]
        else:
            kw = f"concept #{i+1}"
        questions.append(
            f"{i+1}. Explain the concept of **{kw}** in the context of this lecture."
        )

    return (
        f"🧠 *Offline practice quiz* ({difficulty} level)\n\n"
        + "\n".join(questions)
        + "\n\n_Answers depend on the student's understanding; this quiz is meant for self-testing._"
    )


def generate_study_plan(
    store: TfidfStore,
    exam_date: str,
    hours_per_day: int,
    level: str,
    weak_topics: str,
) -> str:
    """
    Offline study plan:
    - Split days until exam
    - Assign sections of the slides to each day
    """
    try:
        exam = datetime.fromisoformat(exam_date).date()
    except Exception:
        exam = date.today() + timedelta(days=7)

    today = date.today()
    days_left = max((exam - today).days, 1)

    # Split content by chunks for each day
    chunks = store.chunks
    if not chunks:
        return "No content available to build a study plan."

    per_day = max(len(chunks) // days_left, 1)

    lines = []
    lines.append(
        f"📅 *Offline study plan* until **{exam.isoformat()}** "
        f"({days_left} day(s) left) – about **{hours_per_day}h/day**, level: **{level}**."
    )
    if weak_topics:
        lines.append(f"⚠️ Focus extra on your weak topics: {weak_topics}")
    lines.append("")

    idx = 0
    for d in range(days_left):
        day_num = d + 1
        start = idx
        end = min(idx + per_day, len(chunks))
        idx = end

        subtopics = []
        for c in chunks[start:end]:
            sent = _first_sentences(c, max_chars=120)
            if sent:
                subtopics.append(f"- {sent}")

        if not subtopics:
            subtopics.append("- Review previous material or do practice problems.")

        lines.append(f"**Day {day_num}:**")
        lines.extend(subtopics)
        lines.append("")

    lines.append("✅ Last day before exam: full review + solve practice questions.")
    lines.append("💡 Tip: study in 25–30 min focused blocks with short breaks.")

    return "\n".join(lines)
