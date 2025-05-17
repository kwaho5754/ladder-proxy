from flask import Flask, jsonify
from flask_cors import CORS
import requests
from collections import Counter

app = Flask(__name__)
CORS(app)

DATA_URL = "https://ntry.com/data/json/games/power_ladder/recent_result.json"

def convert_pattern_name(start, line, odd_even):
    direction = "좌" if start == "LEFT" else "우"
    line_map = {"3": "삼", "4": "사"}
    odd_even_map = {"ODD": "홀", "EVEN": "짝"}
    return f"{direction}{line_map.get(line, '')}{odd_even_map.get(odd_even, '')}"

def transform_to_symmetry(pattern):
    if not pattern or len(pattern) < 3:
        return None
    direction = pattern[0]
    line = pattern[1]
    odd_even = pattern[2:]

    direction_map = {"좌": "우", "우": "좌"}
    line_map = {"삼": "사", "사": "삼"}
    odd_even_map = {"홀": "짝", "짝": "홀"}

    return (
        direction_map.get(direction, "") +
        line_map.get(line, "") +
        odd_even_map.get(odd_even, "")
    )

def predict_block_patterns(pattern_list, position="front"):
    predictions = []
    data_length = len(pattern_list)

    for block_size in range(2, 6):  # 블럭 길이 2~5까지만
        if position == "front":
            base_block = pattern_list[-block_size:]
        elif position == "back":
            base_block = pattern_list[-(block_size + 2):-2]
        else:
            continue

        compare_block = base_block[:block_size * 2 // 3]
        transformed = [transform_to_symmetry(p) for p in compare_block]

        print(f"[DEBUG] position={position} block_size={block_size} base_block={base_block}")
        print(f"[DEBUG] transformed={transformed}")

        if None in transformed or len(transformed) < 1:
            continue

        matched = False
        for j in range(data_length - len(transformed)):
            candidate = pattern_list[j:j + len(transformed)]
            if candidate == transformed:
                matched = True
                if j > 0:
                    predictions.append(pattern_list[j - 1])
        print(f"[DEBUG] matched={matched} total_predictions={len(predictions)}")

    return [p for p in predictions if p]

@app.route("/predict", methods=["GET"])
def predict():
    try:
        response = requests.get(DATA_URL)
        data = response.json()

        pattern_list = [
            convert_pattern_name(item["start_point"], item["line_count"], item["odd_even"])
            for item in data
        ][::-1]

        front = predict_block_patterns(pattern_list, position="front")
        back = predict_block_patterns(pattern_list, position="back")

        front_top5 = [x[0] for x in Counter(front).most_common(5)]
        back_top5 = [x[0] for x in Counter(back).most_common(5)]

        print(f"[FINAL] front_top5: {front_top5}")
        print(f"[FINAL] back_top5: {back_top5}")

        return jsonify({
            "predict_round": len(pattern_list),
            "front_predictions": front_top5,
            "back_predictions": back_top5
        })

    except Exception as e:
        print("[예측 오류]", str(e))
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
