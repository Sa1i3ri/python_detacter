from flask import Flask, request, jsonify

app = Flask(__name__)

@app.route("/read_file", methods=["GET"])
def read_file():
    filename = request.args.get("filename")
    try:
        with open(filename, "r") as file:
            content = file.read()
        return content
    except FileNotFoundError:

        return jsonify({"error": "Requested file not found."}), 404
