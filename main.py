from flask import Flask, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)  # 🔓 모든 출처 허용 (GitHub Pages 등에서 fetch 가능)

@app.route('/predict')
def predict():
    # 예시 응답 - 실제 데이터로 대체 가능
    front = ["우3홀", "좌4홀", "좌3짝", "우4짝", "우5홀"]
    back = ["좌4홀", "우3홀", "우4짝", "좌3홀", "좌2짝"]
    round_number = 199

    return jsonify({
        "front_predictions": front,
        "back_predictions": back,
        "predict_round": round_number
    })

if __name__ == "__main__":
    # 🔧 Railway에서 외부 접근 허용하려면 반드시 아래 설정
    app.run(debug=True, host="0.0.0.0", port=5000)
