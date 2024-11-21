import pickle
from flask import Flask, request, jsonify

app = Flask(__name__)

@app.route("/load", methods=["POST"])
def load_data():

    serialized_data = request.data
    try:

        data = pickle.loads(serialized_data)
        return jsonify({"message": "Data loaded successfully", "data": data})
    except pickle.UnpicklingError as e:
        return jsonify({"error": str(e)}), 400
