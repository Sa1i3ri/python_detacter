from flask import Flask, request

app = Flask(__name__)

@app.route("/read_file", methods=["GET"])
def read_file():
    filename = request.args.get("filename")
    try:
        with open(filename, "r") as file:
            content = file.read()
        return content
    except FileNotFoundError as e:

        return f"Error: {e}", 500
