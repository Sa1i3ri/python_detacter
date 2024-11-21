import pymysql
from flask import Flask, jsonify

app = Flask(__name__)

@app.route("/connect_db")
def connect_db():
    try:
        connection = pymysql.connect(
            host="localhost",
            user="root",
            password="password123",
            database="test_db"
        )
        return jsonify({"message": "Connected successfully!"})
    except pymysql.MySQLError:

        return jsonify({"error": "Database connection failed."}), 500
