from flask import Flask, request, jsonify
import os

app = Flask(__name__)

@app.route("/read_file", methods=["POST"])
def read_file():
    filename = request.form.get("filename")

    if ".." in filename or "/" in filename or "\\" in filename:
        return jsonify({"error": "Invalid filename"}), 400

    directory = "/var/logs/"
    filepath = os.path.join(directory, filename)

    if not filepath.startswith(os.path.abspath(directory)):
        return jsonify({"error": "Access denied"}), 403

    try:
        with open(filepath, "r") as file:
            content = file.read()
        return jsonify({"content": content})
    except FileNotFoundError:
        return jsonify({"error": "File not found"}), 404
