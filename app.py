# app.py
from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
import logging, sys
from datetime import datetime

app = Flask(__name__, static_folder="static", template_folder="templates")
CORS(app)

# basic logging to stdout so App Platform shows it
logging.basicConfig(stream=sys.stdout, level=logging.INFO)
log = logging.getLogger("quantumpulse")

# ---- Algorithm import (safe fallback) --------------------
try:
    from algorithm import run_algorithm
except Exception as e:
    log.exception("algorithm import failed; using fallback: %s", e)

    def run_algorithm(query: str):
        """Minimal fallback so the app still works."""
        q = (query or "").strip()
        score = round(min(len(q) / 100.0, 1.0), 3)
        return {
            "query": q,
            "score": score,
            "explain": "Fallback algorithm: score = length/100",
            "timestamp": datetime.utcnow().isoformat() + "Z",
        }

# ---- Routes ----------------------------------------------
@app.route("/")
def index():
    return render_template("index.html")

@app.route("/about")
def about():
    return render_template("about.html")

@app.route("/news")
def news():
    return render_template("news.html")

@app.route("/results", methods=["POST"])
def results():
    query = request.form.get("query", "")
    result = run_algorithm(query)
    return render_template("results.html", result=result)

# Simple JSON API
@app.route("/api/score", methods=["POST"])
def api_score():
    data = request.get_json(silent=True) or {}
    query = data.get("query", "")
    result = run_algorithm(query)
    return jsonify(result)

# Health endpoint for the platform
@app.route("/healthz")
def healthz():
    return "ok", 200

# Catch‑all error logging (still returns 500)
@app.errorhandler(Exception)
def on_error(err):
    log.exception("Unhandled error: %s", err)
    return ("Internal error", 500)

if __name__ == "__main__":
    # local/dev only
    app.run(host="0.0.0.0", port=8080, debug=False)
