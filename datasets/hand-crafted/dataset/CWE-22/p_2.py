from flask import Flask, request, jsonify
import os

app = Flask(__name__)

@app.route("/delete_file", methods=["POST"])
def delete_file():
    filename = request.form.get("filename")
    directory = "/uploads/"


    if ".." in filename or "/" in filename or "\\" in filename:
        return jsonify({"error": "Invalid filename"}), 400

    filepath = os.path.join(directory, filename)


    if not os.path.abspath(filepath).startswith(os.path.abspath(directory)):
        return jsonify({"error": "Access denied"}), 403

    try:
        os.remove(filepath)
        return jsonify({"message": "File deleted successfully"})
    except FileNotFoundError:
        return jsonify({"error": "File not found"}), 404
