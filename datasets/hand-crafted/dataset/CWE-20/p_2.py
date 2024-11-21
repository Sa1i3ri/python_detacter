from flask import Flask, request, jsonify
import os

app = Flask(__name__)

UPLOAD_FOLDER = "/uploads/"
ALLOWED_EXTENSIONS = {"txt", "jpg", "png", "pdf"}
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def is_allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route("/upload", methods=["POST"])
def upload_file():
    file = request.files.get("file")
    if not file:
        return jsonify({"error": "No file provided"}), 400

    if not is_allowed_file(file.filename):
        return jsonify({"error": "Invalid file type"}), 400

    sanitized_filename = os.path.basename(file.filename)  # Sanitize the filename
    filepath = os.path.join(UPLOAD_FOLDER, sanitized_filename)

    file.save(filepath)
    return jsonify({"message": f"File saved to {filepath}"}), 200
