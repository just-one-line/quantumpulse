from flask import Flask, render_template, request, jsonify
from agent.agent import TradingAgent
from agent.memory import Memory

app = Flask(__name__)

# Initialize memory and agent
memory = Memory()
agent = TradingAgent(memory=memory)

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/api/signal", methods=["POST"])
def signal():
    """
    Receives market data from frontend or API,
    runs the trading agent, and stores/retrieves context.
    """
    data = request.json
    if not data:
        return jsonify({"error": "No input data"}), 400

    # Example: pass price data into the agent
    market_signal = data.get("signal", "no-signal")
    decision = agent.decide(market_signal)

    # Save decision in memory
    memory.add({"input": market_signal, "decision": decision})

    return jsonify({"decision": decision})

@app.route("/api/memory", methods=["GET"])
def get_memory():
    """Return stored memory for debugging/inspection"""
    return jsonify(memory.get_all())

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
