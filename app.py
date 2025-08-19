from flask import Flask, render_template, jsonify, request
import os, time, math, random

app = Flask(__name__)

@app.route("/")
def index():
    return render_template("index.html")

@app.get("/health")
def health():
    return jsonify(status="ok", ts=time.time())

@app.post("/trade")
def trade():
    """
    Minimal MVP endpoint.
    - action: analyze | buy | sell (simulated)
    - stock: ticker, e.g. TSLA
    Returns a stub "history" so the front-end can draw a chart.
    """
    data = request.get_json(silent=True) or {}
    stock = (data.get("stock") or "").upper().strip()
    action = (data.get("action") or "analyze").lower().strip()

    if not stock:
        return jsonify(ok=False, message="Please provide a stock symbol."), 400

    # --- Simulated history series (deterministic per symbol) ---
    seed = sum(ord(c) for c in stock) % 9973
    rng = random.Random(seed)
    base = 50 + (seed % 30)  # base price per symbol
    history = []
    price = float(base)
    for i in range(60):  # 60 points (~1h at 1-min)
        drift = math.sin(i/9.0) * 0.6 + (rng.random()-0.5)*0.4
        price = max(0.5, price + drift)
        history.append({"time": i, "price": round(price, 2)})

    # --- Simple "signal" using last momentum ---
    last = history[-1]["price"]
    prev = history[-6]["price"] if len(history) >= 6 else history[0]["price"]
    momentum = last - prev
    news_trend_conf = 65 + (seed % 20)  # placeholder 65–84%

    # Recommendation heuristic (placeholder)
    if momentum > 0.8:
        reco, strength = "Strong Buy", 85
    elif momentum > 0.2:
        reco, strength = "Buy", 70
    elif momentum < -0.8:
        reco, strength = "Strong Sell", 85
    elif momentum < -0.2:
        reco, strength = "Sell", 70
    else:
        reco, strength = "Hold", 55

    # Simulated action result
    action_msg = {
        "analyze": f"{stock}: {reco} ({strength}
