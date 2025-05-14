from flask import Flask, jsonify
from flask_cors import CORS
import requests
from collections import Counter
from datetime import datetime

app = Flask(__name__)
CORS(app)

# 사다리 시작일 (정확한 시작일로 조정 가능)
START_DATE = datetime.strptime("2024-01-01", "%Y-%m-%d")

def get_data():
    url = "https://ntry.com/data/json/games/power_ladder/recent_result.json"
    response = requests.get(url)
    return response.json()

def combine_pattern(entry):
    start = '좌' if entry['start_point'] == 'LEFT' else '우'
    line = '삼' if entry['line_count'] == '3' else '사'
    oe = '짝' if entry['odd_even'] == 'EVEN' else '홀'
    return start + line + oe

def get_predict_round(data):
    last = data[0]
    today = datetime.strptime(last['reg_date'], "%Y-%m-%d")
    days_elapsed = (today - START_DATE).days
    base_round = days_elapsed * 288
    current_round = int(last['date_round'])
    return base_round + current_round + 1

@app.route("/recent-result", methods=["GET"])
def predict():
    try:
        data = get_data()
        recent = data[:1000]
        patterns = [combine_pattern(d) for d in recent]
        count = Counter(patterns)
        most_common = count.most_common(3)

        predict_round = get_predict_round(data)

        return jsonify({
            "predict_round": predict_round,
            "result": [p[0] for p in most_common]
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(debug=False, host="0.0.0.0", port=5000)
