from flask import Flask, jsonify, request
from flask_cors import CORS
import requests
from collections import Counter

app = Flask(__name__)
CORS(app)

DATA_URL = "https://ntry.com/data/json/games/power_ladder/recent_result.json"

# 패턴 변환 함수
def convert_pattern_name(start, line, odd_even):
    direction = "좌" if start == "LEFT" else "우"
    line_map = {"3": "삼", "4": "사"}
    odd_even_map = {"ODD": "홀", "EVEN": "짝"}
    return f"{direction}{line_map.get(line, '')}{odd_even_map.get(odd_even, '')}"

# 불균형 요소 계산 함수
def get_imbalance_element(patterns):
    dir_seq = [p[0] for p in patterns]
    line_seq = [p[1] for p in patterns]
    oe_seq = [p[2:] for p in patterns]
    dir_gap = abs(dir_seq.count("좌") - dir_seq.count("우"))
    line_gap = abs(line_seq.count("삼") - line_seq.count("사"))
    oe_gap = abs(oe_seq.count("홀") - oe_seq.count("짝"))
    max_gap = max(dir_gap, line_gap, oe_gap)
    if max_gap == dir_gap:
        return "방향"
    elif max_gap == line_gap:
        return "줄수"
    else:
        return "홀짝"

# 4~8줄 기준 정방향 또는 역방향 Top5 패턴 추출
def get_top_patterns(pattern_list, reverse=False):
    candidates = []
    if reverse:
        pattern_list = list(reversed(pattern_list))
    for size in range(4, 9):
        if len(pattern_list) >= size:
            block = pattern_list[:size]
            dir_seq = [p[0] for p in block]
            line_seq = [p[1] for p in block]
            oe_seq = [p[2:] for p in block]
            direction = "우" if dir_seq.count("좌") > dir_seq.count("우") else "좌"
            line = "사" if line_seq.count("삼") > line_seq.count("사") else "삼"
            oe = "홀" if oe_seq.count("짝") > oe_seq.count("홀") else "짝"
            pattern = direction + line + oe
            candidates.append(pattern)
    top5 = [p for p, _ in Counter(candidates).most_common(5)]
    return top5

# Top1~3 흐름 기반 조합 재구성

def generate_combo_from_top3(top3):
    if not top3:
        return "없음"
    dirs = [p[0] for p in top3 if len(p) == 4]
    lines = [p[1] for p in top3 if len(p) == 4]
    oes = [p[2:] for p in top3 if len(p) == 4]
    if not dirs or not lines or not oes:
        return "없음"
    direction = "우" if dirs.count("좌") > dirs.count("우") else "좌"
    line = "사" if lines.count("삼") > lines.count("사") else "삼"
    oe = "홀" if oes.count("짝") > oes.count("홀") else "짝"
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
        pattern_list = [convert_pattern_name(d["start_point"], d["line_count"], d["odd_even"]) for d in data]

        # 정방향 + 역방향 Top5 → 총 10개 후보
        top_patterns_forward = get_top_patterns(pattern_list, reverse=False)
        top_patterns_reverse = get_top_patterns(pattern_list, reverse=True)
        all_candidates = top_patterns_forward + top_patterns_reverse

        # 고유한 Top3 추출
        top3_unique = list(dict.fromkeys(all_candidates))[:3]

        # Top1~3 흐름 기반으로 combo 생성
        combo = generate_combo_from_top3(top3_unique)

        return jsonify({
            "predict_round": predict_round,
            "top3_patterns": top3_unique,
            "combo_suggestion": combo
        })
    except Exception as e:
        return str(e), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
