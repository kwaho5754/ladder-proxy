from flask import Flask, jsonify
from flask_cors import CORS
import requests

app = Flask(__name__)
CORS(app)

DATA_URL = "https://ntry.com/data/json/games/power_ladder/recent_result.json"

# 패턴 변환 함수 (현재는 에러 원인 확인 전이므로 사용 X)
def convert_pattern_name(start, line, odd_even):
    direction = "좌" if start == "LEFT" else "우"
    line_map = {"3": "삼", "4": "사"}
    odd_even_map = {"ODD": "홀", "EVEN": "짝"}
    return f"{direction}{line_map.get(line, '')}{odd_even_map.get(odd_even, '')}"

@app.route("/predict", methods=["GET"])
def predict():
    try:
        response = requests.get(DATA_URL)
        print("[요청 상태]", response.status_code)

        # 전체 JSON 확인
        data = response.json()
        print("[받은 데이터 수]", len(data))
        print("[예시 데이터 1~3개]", data[:3])

        return jsonify({
            "predict_round": len(data),
            "front_predictions": ["(예시)"],
            "back_predictions": ["(예시)"]
        })

    except Exception as e:
        print("[예측 오류 발생]", str(e))
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
