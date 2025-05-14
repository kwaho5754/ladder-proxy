
from flask import Flask, jsonify
import requests
from flask_cors import CORS

app = Flask(__name__)
CORS(app)  # CORS 허용

@app.route("/recent-result")
def proxy():
    url = "https://ntry.com/data/json/games/power_ladder/recent_result.json"
    res = requests.get(url)
    return jsonify(res.json())

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
