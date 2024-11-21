import subprocess
from flask import Flask, request, jsonify

app = Flask(__name__)

@app.route("/ping", methods=["GET"])
def ping():
    ip_address = request.args.get("ip")

    command = f"ping -c 1 {ip_address}"
    try:
        result = subprocess.check_output(command, shell=True, text=True)
        return jsonify({"result": result})
    except subprocess.CalledProcessError as e:
        return jsonify({"error": str(e)}), 400
