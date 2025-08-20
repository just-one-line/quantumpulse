# algorithm.py
from datetime import datetime

def run_algorithm(query: str):
    q = (query or "").strip()
    score = round(min(len(q) / 100.0, 1.0), 3)
    return {
        "query": q,
        "score": score,
        "explain": "Demo scoring based on length of the query.",
        "timestamp": datetime.utcnow().isoformat() + "Z",
    }
