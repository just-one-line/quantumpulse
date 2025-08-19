from flask import Flask

app = Flask(__name__)

@app.route("/")
def home():
    return "Hello from QuantumPulse!"

# Optional health check endpoint for DO
@app.route("/health")
def health():
    return "ok", 200

if __name__ == "__main__":
    # DO expects 8080
    app.run(host="0.0.0.0", port=8080)
