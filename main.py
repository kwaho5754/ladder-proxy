from flask import Flask, jsonify

app = Flask(__name__)  # ← 이 줄이 반드시 있어야 함

@app.route("/recent-result", methods=["GET"])
def recent_result():
    # 예시 응답
    return jsonify({"predictions": ["LEFT", "RIGHT", "LEFT"]})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
