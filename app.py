# app.py
from __future__ import annotations
import os, logging
from flask import (
    Flask, Blueprint, render_template, request, jsonify, redirect, url_for, flash
)
from werkzeug.middleware.proxy_fix import ProxyFix
import algorithm as algo  # local module with analyze_text/analyze_batch

APP_VERSION = os.getenv("QP_VERSION", "1.0.0")

def create_app() -> Flask:
    app = Flask(__name__)
    app.config.update(
        SECRET_KEY=os.getenv("SECRET_KEY", "dev-not-secret"),
        JSON_SORT_KEYS=False,
        APP_VERSION=APP_VERSION,
    )
    # Respect proxy headers on DigitalOcean
    app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)  # type: ignore

    # ---------- PAGES ----------
    pages = Blueprint("pages", __name__)

    @pages.route("/")
    def index():
        return render_template("index.html")

    @pages.route("/about")
    def about():
        return render_template("about.html")

    @pages.route("/news")
    def news():
        articles = [
            {"tag": "Release", "title": f"QuantumPulse v{APP_VERSION}"},
            {"tag": "Roadmap", "title": "Next: async workers & vector DB"},
        ]
        return render_template("news.html", articles=articles)

    @pages.route("/results", methods=["GET", "POST"])
    def results():
        text = result = None
        if request.method == "POST":
            text = (request.form.get("text") or "").strip()
            if not text:
                flash(("warn", "Please paste some text to analyze."))
                return redirect(url_for("pages.results"))
            result = algo.analyze_text(text)
        return render_template("results.html", text=text, result=result)

    app.register_blueprint(pages)

    # ---------- API (versioned) ----------
    api = Blueprint("api", __name__, url_prefix="/api/v1")

    @api.get("/health")
    def health():
        return jsonify({"ok": True, "service": "quantumpulse", "version": APP_VERSION})

    @api.post("/analyze")
    def analyze():
        payload = request.get_json(silent=True) or {}
        if "texts" in payload and isinstance(payload["texts"], list):
            out = algo.analyze_batch(payload["texts"])
        else:
            text = (payload.get("text") or "").strip()
            if not text:
                return jsonify({"error": "Provide 'text' or 'texts'."}), 400
            out = algo.analyze_text(text)
        return jsonify(out)

    app.register_blueprint(api)

    # ---------- Errors ----------
    @app.errorhandler(404)
    def not_found(e):
        return render_template("base.html"), 404

    # ---------- Logging ----------
    level = logging.INFO if os.getenv("FLASK_ENV") == "production" else logging.DEBUG
    logging.basicConfig(level=level, format="%(asctime)s %(levelname)s %(message)s")

    return app

# Local dev entrypoint; DO uses gunicorn via Procfile
if __name__ == "__main__":
    port = int(os.getenv("PORT", "8080"))
    create_app().run(host="0.0.0.0", port=port, debug=True)
