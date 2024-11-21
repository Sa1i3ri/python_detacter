import sqlite3

def setup_database():
    conn = sqlite3.connect("examples.db")
    cursor = conn.cursor()


    cursor.execute("CREATE TABLE IF NOT EXISTS sensitive_data (id INTEGER, secret TEXT)")
    conn.commit()
    print("Database setup completed.")

def main():
    setup_database()

if __name__ == "__main__":
    main()
