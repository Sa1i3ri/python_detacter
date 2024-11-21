from flask import Flask, request, jsonify
import os

app = Flask(__name__)

@app.route("/read_log", methods=["GET"])
def read_log():

    filename = request.args.get("filename")
    directory = "/var/logs/"


    filepath = directory + filename

    try:
        with open(filepath, "r") as file:
            content = file.read()
        return jsonify({"content": content})
    except FileNotFoundError:
        return jsonify({"error": "File not found"}), 404
