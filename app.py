import os
from datetime import datetime, timedelta
from flask import Flask, jsonify, render_template, url_for

app = Flask(__name__)

# ---- simple in‑memory “app info” ----
APP_NAME = "QuantumPulse"
STARTED_AT = datetime.utcnow().isoformat() + "Z"


# ---- helper: placeholder Fed events (to be replaced with live fetch later) ----
def get_upcoming_fed_events():
    """
    TEMPORARY STUB.
    Returns a few upcoming FOMC/Jackson Hole–style items so the UI and API work.
    In a later step we’ll replace this with a real fetcher that parses calendars.
    """
    today = datetime.utcnow().date()
    sample = [
        {
            "title": "FOMC Meeting (Day 1)",
            "type": "FOMC",
            "importance": "high",
            "start_date": (today + timedelta(days=10)).isoformat(),
            "notes": "Policy discussion begins.",
        },
        {
            "title": "FOMC Meeting (Day 2) + Press Conference",
            "type": "FOMC",
            "importance": "high",
            "start_date": (today + timedelta(days=11)).isoformat(),
            "notes": "Statement + press Q&A.",
        },
        {
            "title": "Jackson Hole Economic Symposium",
            "type": "Symposium",
            "importance": "medium",
            "start_date": (today + timedelta(days=35)).isoformat(),
            "notes": "Keynote often market‑moving.",
        },
    ]
    return sample


# ---- pages (kept minimal so nothing breaks) ----
@app.route("/")
def home():
    # Simple inline HTML so it renders even if templates are missing
    return f"""
    <html>
    <head>
      <title>{APP_NAME}</title>
      <meta name="viewport" content="width=device-width, initial-scale=1" />
      <style>
        body {{ background:#0f1115; color:#eee; font-family:system-ui,-apple-system,Segoe UI,Roboto; padding:24px; }}
        a.button {{ display:inline-block; margin:8px 8px 0 0; padding:10px 14px; border:1px solid #444; border-radius:10px; text-decoration:none; color:#eee; }}
        .muted {{ color:#9aa0a6; font-size:14px; }}
        code {{ background:#1a1f2b; padding:2px 6px; border-radius:6px; }}
      </style>
    </head>
    <body>
      <h1>👋 Hello from {APP_NAME}</h1>
      <p class="muted">If you can see this, Flask is running.</p>

      <div>
        <a class="button" href="{url_for('api_fed_events')}">API: Fed Events (JSON)</a>
        <a class="button" href="{url_for('health')}">Health</a>
        <a class="button" href="{url_for('agent_status')}">Agent Status (JSON)</a>
      </div>

      <p class="muted" style="margin-top:16px">We’ll add the UI and live data next.</p>
      <p class="muted">Started at: <code>{STARTED_AT}</code></p>
    </body>
    </html>
    """


@app.route("/health")
def health():
    return jsonify({"ok": True, "app": APP_NAME, "started_at": STARTED_AT})


@app.route("/agent-status")
def agent_status():
    # Placeholder until the real agent is wired up
    return jsonify({
        "agent": "FedWatchAgent",
        "status": "idle",
        "last_run": None,
        "notes": "Awaiting scheduling & live data hookup."
    })


# ---- NEW: API endpoint that returns upcoming Fed/major CB events ----
@app.route("/api/fed-events")
def api_fed_events():
    events = get_upcoming_fed_events()
    return jsonify({
        "source": "placeholder",
        "count": len(events),
        "events": events,
        "generated_at": datetime.utcnow().isoformat() + "Z"
    })


if __name__ == "__main__":
    # For local/Codespaces dev; DO’s App Platform uses Gunicorn via Procfile
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)
