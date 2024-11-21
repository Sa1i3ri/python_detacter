from flask import Flask, request, send_file

app = Flask(__name__)

@app.route("/download", methods=["GET"])
def download():
    filename = request.args.get("filename")
    directory = "/var/files/"


    filepath = directory + filename

    try:
        return send_file(filepath, as_attachment=True)
    except FileNotFoundError:
        return "<p>File not found</p>", 404
