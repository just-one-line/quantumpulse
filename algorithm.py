def _risk_weights(risk: str):
    risk = (risk or "medium").lower()
    tables = {
        "low":    {"cash": 0.30, "bonds": 0.50, "stocks": 0.20},
        "medium": {"cash": 0.20, "bonds": 0.35, "stocks": 0.45},
        "high":   {"cash": 0.05, "bonds": 0.15, "stocks": 0.80},
    }
    return tables.get(risk, tables["medium"])

FOCUS_TICKERS = {
    "ai":          ["NVDA", "MSFT", "GOOGL"],
    "renewables":  ["ENPH", "TSLA", "NEE"],
    "biotech":     ["CRSP", "VRTX", "MRNA"],
    "defensive":   ["KO", "PG", "JNJ"],
}

def recommend_portfolio(risk: str, horizon: int, focuses: list):
    weights = _risk_weights(risk)
    focuses = [f.lower() for f in focuses or []]

    picks = []
    for f in focuses:
        if f in FOCUS_TICKERS:
            picks.append({
                "focus": f,
                "tickers": FOCUS_TICKERS[f],
                "rationale": f"Exposure to {f} trend."
            })

    if not picks:
        picks.append({
            "focus": "broad_market",
            "tickers": ["VOO", "QQQ"],
            "rationale": "Broad exposure via ETFs."
        })

    return {
        "risk": risk,
        "horizon": horizon,
        "weights": weights,
        "picks": picks
    }
