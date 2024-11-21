from flask import Flask, request, jsonify
import os

app = Flask(__name__)
UPLOAD_FOLDER = "/uploads/"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)


MAX_FILE_SIZE = 10 * 1024 * 1024

@app.before_request
def check_file_size():
    content_length = request.content_length
    if content_length and content_length > MAX_FILE_SIZE:
        return jsonify({"error": "File size exceeds limit"}), 413

@app.route("/upload", methods=["POST"])
def upload_file():
    file = request.files.get("file")
    if not file:
        return jsonify({"error": "No file provided"}), 400

    filepath = os.path.join(UPLOAD_FOLDER, file.filename)
    file.save(filepath)
    return jsonify({"message": "File uploaded successfully!"}), 200
