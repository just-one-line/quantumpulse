import os
from flask import Flask, render_template, jsonify, request
from flask_cors import CORS
from datetime import datetime

# our lightweight background agent
from agent import agent as qp_agent

app = Flask(__name__, template_folder="templates", static_folder="static")
CORS(app)

# ---------- Pages ----------
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

@app.route("/agent")
def agent_page():
    return render_template("agent.html")

# ---------- Health ----------
@app.route("/health")
def health():
    return jsonify({"status": "ok", "time": datetime.utcnow().isoformat()})

# ---------- Agent API ----------
@app.route("/api/agent/status", methods=["GET"])
def api_agent_status():
    return jsonify(qp_agent.status())

@app.route("/api/agent/logs", methods=["GET"])
def api_agent_logs():
    limit = int(request.args.get("limit", "200"))
    return jsonify({"logs": qp_agent.get_logs(limit)})

@app.route("/api/agent/start", methods=["POST"])
def api_agent_start():
    cfg = request.get_json(silent=True) or {}
    qp_agent.set_config(cfg)  # merge config
    started = qp_agent.start()
    return jsonify({"started": started, "status": qp_agent.status()})

@app.route("/api/agent/stop", methods=["POST"])
def api_agent_stop():
    stopped = qp_agent.stop()
    return jsonify({"stopped": stopped, "status": qp_agent.status()})

@app.route("/api/agent/config", methods=["GET", "POST"])
def api_agent_config():
    if request.method == "GET":
        return jsonify(qp_agent.get_config())
    data = request.get_json(silent=True) or {}
    qp_agent.set_config(data)
    return jsonify(qp_agent.get_config())

if __name__ == "__main__":
    port = int(os.getenv("PORT", "8080"))
    app.run(host="0.0.0.0", port=port)
