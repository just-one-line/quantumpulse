from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Tuple

from flask import Flask, jsonify, render_template, request, url_for
from flask_cors import CORS

# ---- Try to import your algorithm; provide a safe fallback if it isn't defined yet.
try:
    # Expecting you to have algorithm.py with a function like `score_text`
    # Feel free to rename to your actual function name and signature.
    from algorithm import score_text  # type: ignore
except Exception:
    def score_text(text: str) -> Dict[str, Any]:
        """Fallback scoring if algorithm.py isn't ready. Replace with your real logic."""
        text = (text or "").strip()
        base = 50
        length_bonus = min(len(text) // 20, 50)  # crude placeholder
        return {
            "score": min(base + length_bonus, 100),
            "components": {
                "clarity": min(20 + len(text) // 40, 30),
                "novelty": 15,
                "feasibility": 15,
                "signal": 10,
            },
            "notes": "Fallback algorithm in app.py used. Implement score_text in algorithm.py."
        }


def create_app() -> Flask:
    app = Flask(__name__, static_folder="static", template_folder="templates")
    CORS(app)

    # ---------- Basic Pages
    @app.route("/")
    def home():
        return render_template("index.html")

    @app.route("/about")
    def about():
        return render_template("about.html")

    @app.route("/news")
    def news():
        return render_template("news.html")

    @app.route("/results")
    def results():
        return render_template("results.html")

    # ---------- Health for platform checks
    @app.route("/healthz")
    def healthz():
        return jsonify({"status": "ok"})

    # ---------- API: score/evaluate text
    @app.route("/api/score", methods=["POST"])
    def api_score():
        """
        Expected JSON:
        {
          "text": "your idea / content",
          "meta": { ... optional extra fields ... }
        }
        """
        try:
            payload = request.get_json(silent=True) or {}
            text = (payload.get("text") or "").strip()

            if not text:
                return jsonify({"error": "Missing 'text'"}), 400

            result = score_text(text)  # Your algorithm
            return jsonify({
                "ok": True,
                "result": result
            })
        except Exception as e:
            return jsonify({"ok": False, "error": str(e)}), 500

    # ---------- 404 -> send home (optional; keeps SPA-like nav tidy)
    @app.errorhandler(404)
    def not_found(_):
        return render_template("index.html"), 404

    return app


# Gunicorn entrypoint
app = create_app()

# Local dev runner
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port, debug=True)
