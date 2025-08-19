# algorithm.py
from __future__ import annotations
import math, re, time, hashlib
from collections import Counter
from functools import lru_cache
from typing import Dict, List, Union

ALGO_VERSION = "1.0.0"

_WORD_RE = re.compile(r"[A-Za-z']+")
_STOP = {
    "a","an","and","the","or","of","to","in","on","for","with","as","by","is","are","was","were",
    "it","this","that","these","those","be","at","from","we","you","they","he","she","i","me",
    "my","our","your","their","but","not","so","if","then","than","too","very","can","could",
}
_SENT = {
    "good": 2, "great": 3, "excellent": 3, "amazing": 3, "nice": 1, "positive": 2,
    "happy": 2, "love": 3, "like": 1, "win": 2, "success": 2,
    "bad": -2, "terrible": -3, "awful": -3, "poor": -2, "sad": -2, "hate": -3, "angry": -2,
    "loss": -2, "fail": -2, "bug": -1, "slow": -1, "risk": -1,
}

def _tokenize(text: str) -> List[str]:
    return [w.lower() for w in _WORD_RE.findall(text)]

def _hash_id(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()[:16]

def _syllables(word: str) -> int:
    w = re.sub(r"[^a-z]", "", word.lower())
    if not w: return 0
    groups = re.findall(r"[aeiouy]+", w)
    count = max(1, len(groups))
    if w.endswith("e") and count > 1:
        count -= 1
    return count

def _flesch(text: str) -> float:
    tokens = _tokenize(text)
    if not tokens: return 0.0
    sents = max(1, len(re.findall(r"[.!?]+", text)))
    words = len(tokens)
    syll = sum(_syllables(t) for t in tokens)
    return round(206.835 - 1.015*(words/sents) - 84.6*(syll/words), 2)

def _sentiment(tokens: List[str]) -> float:
    if not tokens: return 0.0
    s = sum(_SENT.get(t, 0) for t in tokens)
    return max(-1.0, min(1.0, s / max(1.0, math.sqrt(len(tokens))*3)))

def _keywords(tokens: List[str], topk: int = 8) -> List[Dict[str, Union[str, int, float]]]:
    freq = Counter(t for t in tokens if t not in _STOP and len(t) > 2)
    if not freq: return []
    total = sum(freq.values())
    return [{"term": w, "count": c, "score": round(c/total, 4)} for w, c in freq.most_common(topk)]

def _entities(text: str, limit: int = 6) -> List[str]:
    ents = re.findall(r"(?:^|[.!?]\s+)(?:[A-Z][a-z]+)?(?:\s+)?([A-Z][a-z]+)", text)
    seen, out = set(), []
    for e in ents:
        if e not in seen:
            seen.add(e); out.append(e)
        if len(out) >= limit: break
    return out

def _label(score: float) -> str:
    return "positive" if score > 0.2 else "negative" if score < -0.2 else "neutral"

@lru_cache(maxsize=1024)
def _analyze_cached(text: str) -> Dict:
    tokens = _tokenize(text)
    s = _sentiment(tokens)
    return {
        "id": _hash_id(text),
        "version": ALGO_VERSION,
        "created_ts": int(time.time()),
        "input": {"length_chars": len(text), "length_tokens": len(tokens)},
        "metrics": {
            "sentiment": {"score": round(s, 3), "label": _label(s)},
            "readability_flesch": _flesch(text),
        },
        "keywords": _keywords(tokens),
        "entities_guess": _entities(text),
    }

def analyze_text(text: str) -> Dict:
    text = (text or "").strip()
    if not text:
        return {"error": "empty"}
    return _analyze_cached(text)

def analyze_batch(texts: List[str]) -> Dict:
    items = [analyze_text(t) for t in texts]
    digest = hashlib.sha256(("|".join(i.get("id","") for i in items)).encode()).hexdigest()[:16]
    return {"version": ALGO_VERSION, "batch_id": digest, "items": items}
