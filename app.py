from __future__ import annotations

import os
from typing import Any, Dict

from flask import Flask, jsonify, render_template, request

# --- Storage bootstrap -------------------------------------------------------
# We only need a simple log sink for the agent. If agent/storage.py exists,
# we’ll use it; otherwise we fall back to an in‑memory stub so the app still runs.
try:
    # If you created agent/storage.py earlier, this import will succeed.
    # It just needs to expose a class with append_log(str) and optionally read_logs().
    from agent.storage import Storage as _Storage  # type: ignore
except Exception:
    class _Storage:  # minimal fallback so app never crashes
        def __init__(self) -> None:
            self._logs: list[str] = []

        def append_log(self, msg: str) -> None:
            self._logs.append(msg)

        def read_logs(self, limit: int = 100) -> list[str]:
            return self._logs[-limit:]


# --- Agent import (this is the critical bit that failed before) --------------
# Thanks to agent/__init__.py exposing TradingAgent, this import is stable now.
from agent import TradingAgent


def create_app() -> Flask:
    app = Flask(__name__)

    # Make sure Flask can find your templates/static (defaults are fine if you kept the structure)
    app.template_folder = os.path.join(os.getcwd(), "templates")
    app.static_folder = os.path.join(os.getcwd(), "static")

    # Shared singletons
    storage = _Storage()
    agent = TradingAgent(storage=storage, config={"interval_seconds": 5})

    # Start the agent on first request if you want it always-on. For now we expose API controls.
    # agent.start()

    # -------------------- PAGES (rendered) --------------------
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

    # -------------------- HEALTH ------------------------------
    @app.route("/health")
    def health():
        return jsonify({"status": "ok"})

    # -------------------- AGENT API ---------------------------
    @app.route("/api/agent/status")
    def agent_status():
        return jsonify(agent.status())

    @app.route("/api/agent/start", methods=["POST"])
    def agent_start():
        agent.start()
        return jsonify({"ok": True, "status": agent.status()})

    @app.route("/api/agent/stop", methods=["POST"])
    def agent_stop():
        agent.stop()
        return jsonify({"ok": True, "status": agent.status()})

    @app.route("/api/agent/config", methods=["POST"])
    def agent_config():
        """
        Accepts JSON, e.g. {"interval_seconds": 3}
        """
        data: Dict[str, Any] = request.get_json(silent=True) or {}
        agent.update_config(data)
        return jsonify({"ok": True, "status": agent.status()})

    # -------------------- LOGS (optional) ---------------------
    @app.route("/api/logs")
    def logs():
        # Only available if your Storage implements read_logs(); fallback returns in-memory list
        try:
            log_list = storage.read_logs(limit=int(request.args.get("limit", 100)))
        except Exception:
            log_list = []
        return jsonify({"logs": log_list})

    return app


# Gunicorn entrypoint: "app:app"
app = create_app()

if __name__ == "__main__":
    # For local debugging
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 8080)), debug=True)
