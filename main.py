import os
import json
import requests
from flask import Flask, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

def fetch_data():
    url = "https://ntry.com/data/json/games/power_ladder/recent_result.json"
    response = requests.get(url)
    return response.json()

def get_block_pattern(item):
    return f"{item['start_point']}{item['line_count']}{'홀' if item['odd_even'] == 'ODD' else '짝'}"

@app.route("/recent-result", methods=["GET"])
def recent_result():
    try:
        data = fetch_data()
        patterns = [get_block_pattern(item) for item in data]

        block_size = 3
        recent_blocks = [patterns[i:i+block_size] for i in range(len(patterns)-block_size+1)]

        target_block = recent_blocks[0]
        top_candidates = []

        for i in range(1, len(recent_blocks)):
            block = recent_blocks[i]
            # 정방향 & 역방향 비교
            if block == target_block or block[::-1] == target_block:
                if i - 1 >= 0:
                    top_candidates.append(patterns[i - 1])  # 상단
                if i + block_size < len(patterns):
                    top_candidates.append(patterns[i + block_size])  # 하단

        from collections import Counter
        prediction = Counter(top_candidates).most_common(3)
        result_patterns = [p[0] for p in prediction]

        return jsonify({
            "predict_round": int(data[0]["date_round"]) + 1,
            "top3_patterns": result_patterns
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
