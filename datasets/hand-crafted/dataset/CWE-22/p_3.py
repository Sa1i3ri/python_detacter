from flask import Flask, request, send_file
import os

app = Flask(__name__)

@app.route("/download", methods=["GET"])
def download():
    filename = request.args.get("filename")
    directory = "/var/files/"


    if ".." in filename or "/" in filename or "\\" in filename:
        return "<p>Invalid filename</p>", 400

    filepath = os.path.join(directory, filename)


    if not os.path.abspath(filepath).startswith(os.path.abspath(directory)):
        return "<p>Access denied</p>", 403

    try:
        return send_file(filepath, as_attachment=True)
    except FileNotFoundError:
        return "<p>File not found</p>", 404
