from flask import Flask, render_template, request

app = Flask(__name__)

@app.route("/")
def home():
    return render_template("index.html")  # your homepage

@app.route("/about")
def about():
    return render_template("about.html")

@app.route("/news")
def news():
    sample_news = [
        {"title": "QuantumPulse alpha live", "url": "#", "date": "Today", "tags": ["platform"], "summary": "Initial MVP deployed."},
        {"title": "Roadmap update", "url": "#", "date": "This week", "tags": ["roadmap"], "summary": "Next: live news ingestion & weighting."},
    ]
    return render_template("news.html", news=sample_news)

@app.route("/results")
def results():
    query = request.args.get("q", "")
    rows = [
        {"name": "TSLA", "score": 0.82},
        {"name": "NVDA", "score": 0.77},
        {"name": "AAPL", "score": 0.64},
    ]
    return render_template("results.html", query=query, rows=rows)

# Health check (handy for DO)
@app.route("/health")
def health():
    return {"status": "ok"}

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
