from flask import Flask, request, jsonify

app = Flask(__name__)

users = {"admin": "password123"}

@app.route("/login", methods=["POST"])
def login():
    username = request.form.get("username")
    password = request.form.get("password")

    try:
        if users[username] == password:
            return jsonify({"message": "Login successful!"})
        else:
            return jsonify({"error": f"Invalid password for user {username}."}), 401
    except KeyError as e:

        return jsonify({"error": f"User {username} does not exist."}), 404
