import subprocess
from flask import Flask, request, jsonify
import re

app = Flask(__name__)

@app.route("/ping", methods=["GET"])
def ping():
    ip_address = request.args.get("ip")


    ip_pattern = re.compile(r"^(?:[0-9]{1,3}\.){3}[0-9]{1,3}$")
    if not ip_pattern.match(ip_address):
        return jsonify({"error": "Invalid IP address"}), 400


    try:
        result = subprocess.check_output(["ping", "-c", "1", ip_address], text=True)
        return jsonify({"result": result})
    except subprocess.CalledProcessError as e:
        return jsonify({"error": str(e)}), 400
