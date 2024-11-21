import yaml
from flask import Flask, request, jsonify

app = Flask(__name__)

@app.route("/load_yaml", methods=["POST"])
def load_yaml():
    yaml_data = request.data
    try:
        data = yaml.safe_load(yaml_data)
        return jsonify({"message": "YAML loaded successfully", "data": data})
    except yaml.YAMLError as e:
        return jsonify({"error": str(e)}), 400