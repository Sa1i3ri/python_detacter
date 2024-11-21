from flask import Flask, request, jsonify

app = Flask(__name__)

users = {"admin": "password123"}

@app.route("/login", methods=["POST"])
def login():
    username = request.form.get("username")
    password = request.form.get("password")

    try:
        if users.get(username) == password:
            return jsonify({"message": "Login successful!"})
        else:

            return jsonify({"error": "Invalid username or password."}), 401
    except Exception:

        return jsonify({"error": "An error occurred during authentication."}), 500
