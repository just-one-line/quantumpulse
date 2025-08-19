from flask import Flask, jsonify, request, render_template
from flask_cors import CORS
from algorithm import run_algorithm  # import the placeholder algorithm

app = Flask(__name__)
CORS(app)

# Routes for UI pages
@app.route("/")
def index():
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

# API route for testing the algorithm
@app.route("/api/run", methods=["POST"])
def api_run():
    try:
        data = request.get_json(force=True)  # parse JSON body
        result = run_algorithm(data)
        return jsonify(result)
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
