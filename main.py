from flask import Flask, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)  # 모든 도메인에서의 요청을 허용

@app.route("/recent-result", methods=["GET"])
def recent_result():
    # 예시 응답 (실제로는 여기에 예측 로직을 넣으면 됩니다)
    data = {
        "predictions": ["LEFT", "RIGHT", "LEFT"]
    }
    return jsonify(data)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
