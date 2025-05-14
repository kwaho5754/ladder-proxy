from flask import Flask, jsonify
from flask_cors import CORS
import requests
from collections import defaultdict, Counter

app = Flask(__name__)
CORS(app)

DATA_URL = "https://ntry.com/data/json/games/power_ladder/recent_result.json"

# 패턴 이름 변환 함수
def convert_pattern_name(start, line, odd_even):
    direction = "좌" if start == "LEFT" else "우"
    line_map = {"3": "삼", "4": "사"}
    odd_even_map = {"ODD": "홀", "EVEN": "짝"}
    return f"{direction}{line_map.get(line, '')}{odd_even_map.get(odd_even, '')}"

# 과거 기준 반복 블럭 분석 기반 예측 (정방향/역방향 포함)
def smart_predict_from_top(data, block_sizes=(3, 4, 5)):
    pattern_list = [convert_pattern_name(d["start_point"], d["line_count"], d["odd_even"]) for d in data]
    next_pattern_counter = Counter()

    for block_size in block_sizes:
        if len(pattern_list) <= block_size:
            continue

        block_followups = defaultdict(list)
        block_counts = Counter()

        for i in range(0, len(pattern_list) - block_size):
            block = tuple(pattern_list[i:i + block_size])
            block_rev = tuple(reversed(block))

            if i + block_size < len(pattern_list):
                next_val = pattern_list[i + block_size]
                block_followups[block].append(next_val)
                block_followups[block_rev].append(next_val)
                block_counts[block] += 1
                block_counts[block_rev] += 1

        if block_counts:
            most_common_block = block_counts.most_common(1)[0][0]
            followup_counter = Counter(block_followups[most_common_block])
            next_pattern_counter.update(followup_counter)

    top3 = [pattern for pattern, _ in next_pattern_counter.most_common(3)]
    return top3

# 회차 계산
def get_predict_round(data):
    try:
        last_round = int(data[0].get("date_round", 0))
        return 1 if last_round >= 288 else last_round + 1
    except:
        return 1

@app.route("/recent-result", methods=["GET"])
def predict():
    try:
        response = requests.get(DATA_URL)
        data = response.json()

        if not data or len(data) < 10:
            return jsonify({"error": "데이터 부족"}), 500

        predict_round = get_predict_round(data)
        top3_patterns = smart_predict_from_top(data, block_sizes=(3, 4, 5))

        return jsonify({
            "predict_round": predict_round,
            "top3_patterns": top3_patterns
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
