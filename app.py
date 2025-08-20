import os
import threading
from flask import Flask, render_template, jsonify

# guarded imports so the app never fails to boot
try:
    from agent.agent import TradingAgent
except Exception:
    TradingAgent = None

try:
    from agent.storage import Storage
except Exception:
    Storage = None

app = Flask(__name__, template_folder="templates", static_folder="static")

# --- init components safely --------------------------------------------------
storage = Storage() if Storage else None
agent = TradingAgent(storage=storage) if TradingAgent else None

def safe_get_results(limit=60):
    try:
        if storage and hasattr(storage, "get_recent_results"):
            return storage.get_recent_results(limit=limit) or []
        if storage and hasattr(storage, "load_results"):
            return storage.load_results(limit=limit) or []
    except Exception:
        pass
    return []

# --- optional background thread ---------------------------------------------
_bg_thread = None
def maybe_start_background_agent():
    global _bg_thread
    if not agent:
        return
    if os.getenv("ENABLE_AGENT", "0") != "1":
        return
    if _bg_thread and _bg_thread.is_alive():
        return

    def loop():
        try:
            agent.run_forever(interval_seconds=int(os.getenv("AGENT_INTERVAL", "300")))
        except Exception:
            # swallow to avoid crashing container; check logs if needed
            pass

    _bg_thread = threading.Thread(target=loop, daemon=True)
    _bg_thread.start()

maybe_start_background_agent()

# --- routes ------------------------------------------------------------------
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
    return render_template("results.html", results=safe_get_results(limit=60))

# Diagnostics
@app.route("/health")
def health():
    return jsonify({"status": "ok"})

@app.route("/api/agent/status")
def api_agent_status():
    st = {"loaded": bool(agent)}
    if agent:
        try:
            st.update(agent.status())
        except Exception:
            st["status"] = "error"
    return jsonify(st)

@app.route("/api/agent/run_once", methods=["POST", "GET"])
def api_agent_run_once():
    if not agent:
        return jsonify({"ok": False, "error": "agent-not-loaded"}), 500
    out = agent.run_once()
    return jsonify({"ok": True, "result": out})

@app.route("/api/results")
def api_results():
    return jsonify({"results": safe_get_results(limit=200)})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", 8080)))
