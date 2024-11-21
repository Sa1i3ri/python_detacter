from flask import Flask, request, jsonify
import os

app = Flask(__name__)

@app.route("/delete_file", methods=["POST"])
def delete_file():

    filename = request.form.get("filename")
    directory = "/uploads/"


    filepath = directory + filename

    try:
        os.remove(filepath)
        return jsonify({"message": "File deleted successfully"})
    except FileNotFoundError:
        return jsonify({"error": "File not found"}), 404
