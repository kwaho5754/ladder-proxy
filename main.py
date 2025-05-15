from flask import Flask, jsonify
from flask_cors import CORS
import requests
from collections import Counter

app = Flask(__name__)
CORS(app)

DATA_URL = "https://ntry.com/data/json/games/power_ladder/recent_result.json"

# 패턴 이름 변환 함수
def convert_pattern_name(start, line, odd_even):
    direction = "좌" if start == "LEFT" else "우"
    line_map = {"3": "삼", "4": "사"}
    odd_even_map = {"ODD": "홀", "EVEN": "짝"}
    return f"{direction}{line_map.get(line, '')}{odd_even_map.get(odd_even, '')}"

# 블럭 기반 예측: 정방향/역방향 + 위/아래 모두 반영
def smart_predict_from_recent(data, block_sizes=(3, 4, 5)):
    pattern_list = [convert_pattern_name(d["start_point"], d["line_count"], d["odd_even"]) for d in data]
    next_pattern_counter = Counter()

    for block_size in block_sizes:
        if len(pattern_list) <= block_size:
            continue

        current_block = pattern_list[:block_size]
        current_block_rev = list(reversed(current_block))

        for i in range(0, len(pattern_list) - block_size):
            past_block = pattern_list[i:i + block_size]
            if past_block == current_block or past_block == current_block_rev:
                # 블럭 다음줄(아래값)
                if i + block_size < len(pattern_list):
                    next_val = pattern_list[i + block_size]
                    next_pattern_counter[next_val] += 1
                # 블럭 이전줄(위값)
                if i - 1 >= 0:
                    prev_val = pattern_list[i - 1]
                    next_pattern_counter[prev_val] += 1

    # 예측값 상위 3개 반환 (없으면 '없음' 대체)
    top3 = [pattern for pattern, _ in next_pattern_counter.most_common(3)]
    while len(top3) < 3:
        top3.append("없음")
    return top3

# 다음 회차 계산
def get_predict_round(data):
    try:
        last_round = int(data[0].get("date_round", 0))
        return 1 if last_round >= 288 else last_round + 1
    except:
        return 1

# API 경로: /recent-result
@app.route("/recent-result", methods=["GET"])
def predict():
    try:
        response = requests.get(DATA_URL)
        data = response.json()

        if not data or len(data) < 10:
            return jsonify({"error": "데이터 부족"}), 500

        predict_round = get_predict_round(data)
        top3_patterns = smart_predict_from_recent(data, block_sizes=(3, 4, 5))

        return jsonify({
            "predict_round": predict_round,
            "top3_patterns": top3_patterns
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# 서버 실행
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
