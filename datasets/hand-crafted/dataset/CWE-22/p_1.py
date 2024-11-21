from flask import Flask, request, jsonify
import os

app = Flask(__name__)

@app.route("/read_log", methods=["GET"])
def read_log():
    filename = request.args.get("filename")
    directory = "/var/logs/"


    if ".." in filename or "/" in filename or "\\" in filename:
        return jsonify({"error": "Invalid filename"}), 400

    filepath = os.path.join(directory, filename)


    if not os.path.abspath(filepath).startswith(os.path.abspath(directory)):
        return jsonify({"error": "Access denied"}), 403

    try:
        with open(filepath, "r") as file:
            content = file.read()
        return jsonify({"content": content})
    except FileNotFoundError:
        return jsonify({"error": "File not found"}), 404
