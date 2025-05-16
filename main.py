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

# 요소별 블럭 기반 균형 조합 계산
def predict_by_balance_combo(data):
    pattern_list = [convert_pattern_name(d["start_point"], d["line_count"], d["odd_even"]) for d in data]
    block_size = 8
    if len(pattern_list) < block_size:
        return "없음"
    recent_block = pattern_list[:block_size]
    dir_seq = [p[0] for p in recent_block]
    line_seq = [p[1] for p in recent_block]
    oe_seq = [p[2:] for p in recent_block]
    direction = "우" if dir_seq.count("좌") > dir_seq.count("우") else "좌"
    line = "사" if line_seq.count("삼") > line_seq.count("사") else "삼"
    oe = "홀" if oe_seq.count("짝") > oe_seq.count("홀") else "짝"
    return direction + line + oe

# 예측 함수 (Top3: 6줄, 4줄, 2줄 기준)
def smart_predict_from_recent(data):
    pattern_list = [convert_pattern_name(d["start_point"], d["line_count"], d["odd_even"]) for d in data]
    candidates = []

    def extract_combo(block_size):
        if len(pattern_list) < block_size:
            return "없음"
        block = pattern_list[:block_size]
        dir_seq = [p[0] for p in block]
        line_seq = [p[1] for p in block]
        oe_seq = [p[2:] for p in block]
        direction = "우" if dir_seq.count("좌") > dir_seq.count("우") else "좌"
        line = "사" if line_seq.count("삼") > line_seq.count("사") else "삼"
        oe = "홀" if oe_seq.count("짝") > oe_seq.count("홀") else "짝"
        return direction + line + oe

    top1 = extract_combo(6)
    top2 = extract_combo(4)
    top3 = extract_combo(2)

    return [top1, top2, top3]

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
        combo = predict_by_balance_combo(data)
        top3 = smart_predict_from_recent(data)
        return jsonify({
            "predict_round": predict_round,
            "top3_patterns": top3,
            "combo_suggestion": combo
        })
    except Exception as e:
        return str(e), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
