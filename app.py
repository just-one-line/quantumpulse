from flask import Flask, jsonify, request, render_template
from flask_cors import CORS
import os, json
from algorithm import recommend_portfolio

app = Flask(__name__, static_folder="static", template_folder="templates")
CORS(app)

@app.route("/")
def index():
    # serves the frontend dashboard
    return render_template("index.html")

@app.route("/api/health")
def health():
    return jsonify(status="ok")

@app.route("/api/news")
def news():
    topic = (request.args.get("topic") or "all").lower()
    data_path = os.path.join("data", "news.json")
    try:
        with open(data_path, "r", encoding="utf-8") as f:
            items = json.load(f)
    except Exception:
        items = []

    if topic != "all":
        items = [
            n for n in items
            if topic in n.get("title", "").lower()
            or topic in " ".join(n.get("tags", [])).lower()
        ]
    return jsonify(items=items[:20])

@app.route("/api/recommend", methods=["POST"])
def recommend():
    payload = request.get_json(force=True) or {}
    risk = (payload.get("risk") or "medium").lower()
    horizon = int(payload.get("horizon") or 12)
    focus = payload.get("focus") or []
    result = recommend_portfolio(risk=risk, horizon=horizon, focuses=focus)
    return jsonify(result)

@app.route("/api/feedback", methods=["POST"])
def feedback():
    os.makedirs("data", exist_ok=True)
    entry = {"payload": request.get_json(force=True) or {}}
    with open(os.path.join("data", "feedback.log"), "a", encoding="utf-8") as f:
        f.write(json.dumps(entry) + "\n")
    return jsonify(ok=True)

if __name__ == "__main__":
    # Gunicorn will run this by default in App Platform (app:app)
    app.run(host="0.0.0.0", port=8080)
