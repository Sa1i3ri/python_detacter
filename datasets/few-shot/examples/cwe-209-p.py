import sqlite3
import logging

logging.basicConfig(filename="app.log", level=logging.ERROR)

def get_user_info(user_id):
    try:
        connection = sqlite3.connect("example.db")
        cursor = connection.cursor()
        query = "SELECT * FROM users WHERE id = ?"
        cursor.execute(query, (user_id,))
        result = cursor.fetchall()
        connection.close()
        return result
    except Exception as e:
        # Secure: Log the detailed error message and return a generic error to the user
        logging.error(f"An internal error occurred: {e}")
        return "An error occurred. Please try again later."

user_id = input("Enter user ID: ")
print(get_user_info(user_id))
