import os, time, json
from flask import Flask, request, jsonify

APP_ENV = os.getenv("APP_ENV", "prod")
TV_SECRET = os.getenv("TV_WEBHOOK_SECRET", "")  # set in DO App Settings
JWT_SECRET = os.getenv("JWT_SECRET", "change_me")

app = Flask(__name__)

@app.get("/health")
def health():
    return jsonify(status="ok", env=APP_ENV, time=time.time())

@app.post("/tv-webhook")
def tv_webhook():
    # Accept secret via header or JSON field
    provided = request.headers.get("X-TV-Secret") or request.json.get("secret")
    if not TV_SECRET or provided != TV_SECRET:
        return jsonify(ok=False, error="Invalid secret"), 401

    payload = request.json or {}
    # TODO: enqueue for pending orders / safety checks / broker integration
    return jsonify(ok=True, received=payload, note="Stub: webhook received")

@app.get("/settings")
def settings():
    # Minimal placeholder settings
    return jsonify({
        "strategies": {
            "MarketSwingAI": {"allocation": 0.5},
            "SnapbackLogic": {"allocation": 0.3},
            "RossCameron": {"allocation": 0.2}
        },
        "safety_revert": {"per_trade_loss": 0.05, "daily_drawdown": 0.08}
    })

# For local testing only:
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
