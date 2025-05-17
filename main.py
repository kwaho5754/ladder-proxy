from flask import Flask, jsonify
from collections import Counter
import requests

app = Flask(__name__)

@app.route("/predict")
def predict():
    try:
        # JSON 데이터 요청 (최근 288개 결과)
        url = "https://ntry.com/data/json/games/power_ladder/recent_result.json"
        res = requests.get(url)
        data = res.json()

        # 결과값만 추출
        results = [item['result'] for item in data['rows'] if 'result' in item]

        # 예측값 빈도 수 세기
        count = Counter(results)
        top_10 = [item[0] for item in count.most_common(10)]

        response = {
            "front_predictions": top_10[:5],
            "back_predictions": top_10[5:],
            "predict_round": len(results)
        }
        return jsonify(response)

    except Exception as e:
        print("[ERROR]", str(e))
        return jsonify({
            "front_predictions": [],
            "back_predictions": [],
            "predict_round": 0
        })

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
