import os
from flask import Flask, render_template, jsonify

# Optional imports guarded so the app never crashes if agent/storage change
try:
    from agent.agent import TradingAgent
except Exception:  # pragma: no cover
    TradingAgent = None

try:
    from agent.storage import Storage
except Exception:  # pragma: no cover
    Storage = None

app = Flask(__name__, template_folder="templates", static_folder="static")

# --- Init backend components safely -----------------------------------------
storage = None
if Storage is not None:
    try:
        storage = Storage()
    except Exception:
        storage = None

agent = None
if TradingAgent is not None:
    try:
        agent = TradingAgent(storage=storage)
    except Exception:
        agent = None


def safe_get_results(limit: int = 50):
    """
    Try a few common ways to fetch recent results without throwing.
    Return a list (possibly empty).
    """
    try:
        if storage and hasattr(storage, "get_recent_results"):
            data = storage.get_recent_results(limit=limit)
            return data or []
        if storage and hasattr(storage, "load_results"):
            data = storage.load_results(limit=limit)
            return data or []
    except Exception:
        pass
    # Fallback: look for a simple JSONL file written by the agent
    path = os.getenv("RESULTS_PATH", "data/results.jsonl")
    items = []
    if os.path.exists(path):
        try:
            import json
            with open(path, "r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if line:
                        items.append(json.loads(line))
        except Exception:
            return []
    return items[-limit:]


# --- Routes ------------------------------------------------------------------
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
    data = safe_get_results(limit=60)
    # Never crash the page; always render the template
    return render_template("results.html", results=data)

# Health and diagnostics
@app.route("/health")
def health():
    return jsonify({"status": "ok"})

@app.route("/api/agent/status")
def agent_status():
    status = {"loaded": bool(agent)}
    if hasattr(agent, "status"):
        try:
            status.update(agent.status())
        except Exception:
