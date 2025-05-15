from flask import Flask, jsonify
from flask_cors import CORS
import requests
from collections import Counter

app = Flask(__name__)
CORS(app)

DATA_URL = "https://ntry.com/data/json/games/power_ladder/recent_result.json"

# 패턴 이름 변환
def convert_pattern_name(start, line, odd_even):
    direction = "좌" if start == "LEFT" else "우"
    line_map = {"3": "삼", "4": "사"}
    odd_even_map = {"ODD": "홀", "EVEN": "짝"}
    return f"{direction}{line_map.get(line, '')}{odd_even_map.get(odd_even, '')}"

# 가중치 기반 예측 로직
def smart_predict_from_recent(data):
    pattern_list = [convert_pattern_name(d["start_point"], d["line_count"], d["odd_even"]) for d in data]
    score_counter = Counter()

    # 최신 블럭 (5~3줄 블럭 순차적으로)
    for block_size in (5, 4, 3):
        if len(pattern_list) <= block_size:
            continue

        current_block = pattern_list[:block_size]
        current_block_rev = list(reversed(current_block))

        # 점수 정의
        forward_score = {5: 5, 4: 3, 3: 2}[block_size]
        reverse_score = {5: 4, 4: 2, 3: 1}[block_size]

        for i in range(0, len(pattern_list) - block_size):
            past_block = pattern_list[i:i + block_size]

            match_score = 0
            if past_block == current_block:
                match_score = forward_score
            elif past_block == current_block_rev:
                match_score = reverse_score

            if match_score > 0:
                # 블럭 다음 줄(아래)
                if i + block_size < len(pattern_list):
                    next_val = pattern_list[i + block_size]
                    score_counter[next_val] += match_score + 1  # +1은 아래줄 점수
                # 블럭 이전 줄(위)
                if i - 1 >= 0:
                    prev_val = pattern_list[i - 1]
                    score_counter[prev_val] += match_score + 1  # +1은 위줄 점수

    # 상위 3개 결과 반환 (없으면 '없음' 추가)
    top3 = [pattern for pattern, _ in score_counter.most_common(3)]
    while len(top3) < 3:
        top3.append("없음")
    return top3

# 예측 회차 계산
def get_predict_round(data):
    try:
        last_round = int(data[0].get("date_round", 0))
        return 1 if last_round >= 288 else last_round + 1
    except:
        return 1

# 웹 API 엔드포인트
@app.route("/recent-result", methods=["GET"])
def predict():
    try:
        response = requests.get(DATA_URL)
        data = response.json()

        if not data or len(data) < 10:
            return jsonify({"error": "데이터 부족"}), 500

        predict_round = get_predict_round(data)
        top3_patterns = smart_predict_from_recent(data)

        return jsonify({
            "predict_round": predict_round,
            "top3_patterns": top3_patterns
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
