"""
Conversation Analysis Module
------------------------------
Analyzes the customer's claim description and conversation transcript for:
    - Contradictions between statements
    - Repeated / copy-pasted patterns
    - Suspicious keywords
    - Overall consistency

Output:
    Conversation Trust Score (0-100, higher = more trustworthy)
"""

import os
import re
from typing import Dict, List

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


SUSPICIOUS_KEYWORDS = [
    "guarantee payout", "no questions asked", "cash only",
    "don't tell", "off the record", "untraceable",
    "friend in the company", "quick settlement",
]

CONTRADICTION_PAIR_HINTS = [
    ("day", "night"),
    ("alone", "with"),
    ("parked", "moving"),
    ("new", "old"),
]


def _read_transcript(conversation_path: str) -> List[str]:
    if not conversation_path or not os.path.exists(conversation_path):
        return []
    with open(conversation_path, "r", encoding="utf-8") as f:
        lines = [line.strip() for line in f.readlines() if line.strip()]
    return lines


def _detect_suspicious_keywords(text: str) -> List[str]:
    text_lower = text.lower()
    return [kw for kw in SUSPICIOUS_KEYWORDS if kw in text_lower]


def _detect_repeated_lines(lines: List[str]) -> int:
    """Counts near-duplicate lines, which can indicate scripted/copy-pasted statements."""
    seen = set()
    repeats = 0
    for line in lines:
        normalized = re.sub(r"\s+", " ", line.lower().strip())
        if normalized in seen:
            repeats += 1
        seen.add(normalized)
    return repeats


def _detect_contradictions(lines: List[str]) -> int:
    """Lightweight heuristic: flags lines that contain opposing terms across the transcript."""
    joined = " ".join(lines).lower()
    contradictions = 0
    for term_a, term_b in CONTRADICTION_PAIR_HINTS:
        if term_a in joined and term_b in joined:
            contradictions += 1
    return contradictions


def _consistency_score(claim_description: str, lines: List[str]) -> float:
    """
    Uses TF-IDF + cosine similarity to measure how consistent the claim
    description is with the conversation transcript. Returns a 0-1 score.
    """
    if not lines:
        return 0.5  # neutral score when there is nothing to compare against

    documents = [claim_description] + lines
    vectorizer = TfidfVectorizer(stop_words="english")
    try:
        tfidf_matrix = vectorizer.fit_transform(documents)
    except ValueError:
        return 0.5  # empty vocabulary fallback

    similarities = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:])
    return float(similarities.mean())


def analyze_conversation(claim_description: str, conversation_path: str) -> Dict:
    """
    Analyze the conversation transcript alongside the claim description.

    Returns:
        dict with keys: trust_score, suspicious_keywords, repeated_lines,
        contradiction_flags, consistency_ratio
    """
    lines = _read_transcript(conversation_path)
    full_text = claim_description + " " + " ".join(lines)

    suspicious = _detect_suspicious_keywords(full_text)
    repeats = _detect_repeated_lines(lines)
    contradictions = _detect_contradictions(lines)
    consistency = _consistency_score(claim_description, lines)

    # Start from a perfect score and deduct for each red flag
    score = 100
    score -= len(suspicious) * 15
    score -= repeats * 10
    score -= contradictions * 20
    score -= int((1 - consistency) * 20)
    score = max(0, min(100, score))

    return {
        "trust_score": score,
        "suspicious_keywords": suspicious,
        "repeated_lines": repeats,
        "contradiction_flags": contradictions,
        "consistency_ratio": round(consistency, 2),
    }
