from flask import Flask, request, jsonify
import os

app = Flask(__name__)

@app.route("/read_file", methods=["POST"])
def read_file():
    filename = request.form.get("filename")

    directory = "/var/logs/"
    filepath = directory + filename

    try:
        with open(filepath, "r") as file:
            content = file.read()
        return jsonify({"content": content})
    except FileNotFoundError:
        return jsonify({"error": "File not found"}), 404
