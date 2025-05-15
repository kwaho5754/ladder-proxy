import os
import requests
from flask import Flask, jsonify
from flask_cors import CORS
from collections import Counter

app = Flask(__name__)
CORS(app)

DATA_URL = "https://ntry.com/data/json/games/power_ladder/recent_result.json"

def convert_pattern_name(start, line, odd_even):
    direction = "좌" if start == "LEFT" else "우"
    line_map = {"3": "삼", "4": "사"}
    odd_even_map = {"ODD": "홀", "EVEN": "짝"}
    return f"{direction}{line_map.get(line, '')}{odd_even_map.get(odd_even, '')}"

def fetch_data():
    response = requests.get(DATA_URL)
    return response.json()

def predict_bidirectional(data, block_sizes=(3, 4, 5)):
    pattern_list = [convert_pattern_name(d["start_point"], d["line_count"], d["odd_even"]) for d in data]
    next_pattern_counter = Counter()

    for block_size in block_sizes:
        if len(pattern_list) <= block_size:
            continue

        current_block = pattern_list[:block_size]
        current_block_rev = current_block[::-1]

        for i in range(len(pattern_list) - block_size):
            past_block = pattern_list[i:i + block_size]
            if past_block == current_block or past_block == current_block_rev:
                if i + block_size < len(pattern_list):
                    next_pattern_counter[pattern_list[i + block_size]] += 1  # 아래쪽
                if i - 1 >= 0:
                    next_pattern_counter[pattern_list[i - 1]] += 1  # 위쪽

    return [pattern for pattern, _ in next_pattern_counter.most_common(3)]

def get_predict_round(data):
    try:
        last_round = int(data[0].get("date_round", 0))
        return 1 if last_round >= 288 else last_round + 1
    except:
        return 1

@app.route("/recent-result", methods=["GET"])
def recent_result():
    try:
        data = fetch_data()
        if not data or len(data) < 10:
            return jsonify({"error": "데이터 부족"}), 500

        predict_round = get_predict_round(data)
        top3_patterns = predict_bidirectional(data, block_sizes=(3, 4, 5))

        return jsonify({
            "predict_round": predict_round,
            "top3_patterns": top3_patterns
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
