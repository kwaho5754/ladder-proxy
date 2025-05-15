from flask import Flask, jsonify
from flask_cors import CORS
import csv
from collections import Counter

app = Flask(__name__)
CORS(app)

CSV_FILE_PATH = "ladder_results.csv"
BLOCK_SIZES = [3, 4, 5]

def read_csv_data():
    with open(CSV_FILE_PATH, "r", encoding="utf-8") as file:
        reader = csv.reader(file)
        return list(reader)

def extract_patterns(data, block_size):
    result_patterns = []
    if len(data) <= block_size:
        return result_patterns

    current_block = data[-block_size:]  # 최신 블럭 기준
    reversed_block = current_block[::-1]

    for i in range(len(data) - block_size):
        compare_block = data[i:i + block_size]
        before_index = i - 1
        after_index = i + block_size

        if compare_block == current_block:
            if after_index < len(data):
                result_patterns.append(data[after_index][0])
        if compare_block == reversed_block:
            if after_index < len(data):
                result_patterns.append(data[after_index][0])
        if compare_block == current_block:
            if before_index >= 0:
                result_patterns.append(data[before_index][0])
        if compare_block == reversed_block:
            if before_index >= 0:
                result_patterns.append(data[before_index][0])

    return result_patterns

def predict_top_patterns(data):
    all_predictions = []
    for block_size in BLOCK_SIZES:
        all_predictions += extract_patterns(data, block_size)

    if not all_predictions:
        return []

    counter = Counter(all_predictions)
    return [item[0] for item in counter.most_common(3)]

def get_next_round(data):
    if not data:
        return 1
    last_round = int(data[-1][3])
    return last_round + 1

@app.route("/recent-result", methods=["GET"])
def get_prediction():
    data = read_csv_data()
    top3 = predict_top_patterns(data)
    next_round = get_next_round(data)
    return jsonify({
        "predict_round": next_round,
        "top3_patterns": top3
    })

if __name__ == "__main__":
    app.run(debug=False)
