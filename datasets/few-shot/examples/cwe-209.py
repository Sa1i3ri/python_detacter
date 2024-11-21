import sqlite3

def get_user_info(user_id):
    try:
        connection = sqlite3.connect("example.db")
        cursor = connection.cursor()
        query = f"SELECT * FROM users WHERE id = {user_id}"
        cursor.execute(query)
        result = cursor.fetchall()
        connection.close()
        return result
    except Exception as e:
        # Vulnerable: Directly exposing the exception to the user
        return f"An error occurred: {e}"

user_id = input("Enter user ID: ")
print(get_user_info(user_id))
