from flask import Flask, render_template, request, jsonify
from datetime import datetime

# --- Agent imports ---
try:
    from agent.agent import TradingAgent
except Exception as e:
    TradingAgent = None
    _agent_import_error = str(e)

app = Flask(__name__)

# Create a single agent instance (if available)
agent = TradingAgent() if TradingAgent else None

# ---------- Web pages ----------
@app.route("/")
def home():
    return render_template("index.html")

@app.route("/about")
def about():
    # Only render if template exists; otherwise show a minimal page
    try:
        return render_template("about.html")
    except Exception:
        return "<h1>About</h1><p>Coming soon.</p>"

@app.route("/news")
def news():
    try:
        return render_template("news.html")
    except Exception:
        return "<h1>News</h1><p>Coming soon.</p>"

@app.route("/results")
def results():
    try:
        return render_template("results.html")
    except Exception:
        return "<h1>Results</h1><p>Coming soon.</p>"

@app.route("/agent")
def agent_ui():
    """Simple page to view agent memory and run a test analysis."""
    # Fallback text if Jinja template doesn't exist
    try:
        return render_template("agent.html")
    except Exception:
        if agent is None:
            return f"<h1>Agent</h1><p>Import error: {_agent_import_error}</p>"
        mem = agent.get_recent_memory(20)
        items = "".join(f"<li>{m}</li>" for m in mem)
        return f"""
            <h1>Agent Memory</h1>
            <ul>{items}</ul>
            <form method="post" action="/agent/run"><button>Run test analysis</button
