from flask import Flask, jsonify, render_template_string, request
from flask_cors import CORS
import requests
from collections import Counter

app = Flask(__name__)
CORS(app)

DATA_URL = "https://ntry.com/data/json/games/power_ladder/recent_result.json"

# 결과 패턴 이름 변환
def convert_pattern_name(start, line, odd_even):
    direction = "좌" if start == "LEFT" else "우"
    line_map = {"3": "삼", "4": "사"}
    odd_even_map = {"ODD": "홀", "EVEN": "짝"}
    return f"{direction}{line_map.get(line, '')}{odd_even_map.get(odd_even, '')}"

# 전환 패턴 사전 정의
def get_transition_patterns(pattern):
    transitions = {
        "우사짝": ["우삼홀", "좌삼짝", "좌사홀"],
        "좌삼홀": ["우삼홀", "우사짝", "좌사짝"],
        "우사홀": ["좌사홀", "우삼홀", "좌삼짝"],
        "좌사홀": ["좌삼짝", "우사짝", "우삼홀"],
        "좌삼짝": ["우사짝", "좌사짝", "우삼홀"],
        "우삼홀": ["우사짝", "좌삼짝", "좌사짝"],
    }
    return transitions.get(pattern, [])

# 대칭 패턴 생성
def get_symmetric_pattern(pattern):
    direction_map = {"좌": "우", "우": "좌"}
    line_map = {"삼": "삼", "사": "사"}
    odd_even_map = {"홀": "짝", "짝": "홀"}
    if len(pattern) != 4:
        return None
    direction = pattern[0]
    line = pattern[1]
    oe = pattern[2:]
    new_dir = direction_map.get(direction, "")
    new_line = line_map.get(line, "")
    new_oe = odd_even_map.get(oe, "")
    return new_dir + new_line + new_oe if new_dir and new_line and new_oe else None

# 예측 함수 (기존 방식)
def smart_predict_from_recent(data):
    pattern_list = [convert_pattern_name(d["start_point"], d["line_count"], d["odd_even"]) for d in data]
    score_counter = Counter()
    for block_size in (5, 4, 3):
        if len(pattern_list) <= block_size:
            continue
        current_block = pattern_list[:block_size]
        current_block_rev = list(reversed(current_block))
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
                candidates = []
                if i + block_size < len(pattern_list):
                    candidates.append(pattern_list[i + block_size])
                if i - 1 >= 0:
                    candidates.append(pattern_list[i - 1])
                for c in candidates:
                    score_counter[c] += match_score + 1
                    for alt in get_transition_patterns(c):
                        score_counter[alt] += 1
                    sym = get_symmetric_pattern(c)
                    if sym:
                        score_counter[sym] += 1
    top3 = [pattern for pattern, _ in score_counter.most_common(3)]
    while len(top3) < 3:
        top3.append("없음")
    return top3

# 요소별 밸런스 조합 추천
def predict_by_balance_combo(data):
    pattern_list = [convert_pattern_name(d["start_point"], d["line_count"], d["odd_even"]) for d in data[:100]]
    dir_count = Counter([p[0] for p in pattern_list])
    line_count = Counter([p[1] for p in pattern_list])
    oe_count = Counter([p[2:] for p in pattern_list])
    direction = "우" if dir_count["좌"] > dir_count["우"] else "좌"
    line = "사" if line_count["삼"] > line_count["사"] else "삼"
    oe = "홀" if oe_count["짝"] > oe_count["홀"] else "짝"
    return direction + line + oe

# 예측 회차 계산
def get_predict_round(data):
    try:
        last_round = int(data[0].get("date_round", 0))
        return 1 if last_round >= 288 else last_round + 1
    except:
        return 1

@app.route("/predict", methods=["GET"])
def predict():
    try:
        response = requests.get(DATA_URL)
        data = response.json()
        if not data or len(data) < 10:
            return "데이터 부족"
        predict_round = get_predict_round(data)
        top3 = smart_predict_from_recent(data)
        combo = predict_by_balance_combo(data)
        return render_template_string("""
        <h2>혜칙 실행</h2>
        <button onclick="window.location.reload()">예칙 실행</button><br><br>
        예칙 회차: {{ round }}회차<br>
        1위: {{ top3[0] }}<br>
        2위: {{ top3[1] }}<br>
        3위: {{ top3[2] }}<br><br>
        <strong>관찰 조합 차점을 고려한 예칙: {{ combo }}</strong>
        """, round=predict_round, top3=top3, combo=combo)
    except Exception as e:
        return str(e)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
