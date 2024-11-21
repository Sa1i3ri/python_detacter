import hashlib

def store_password(password):

    hashed_password = hashlib.md5(password.encode()).hexdigest()
    print(f"Stored password hash: {hashed_password}")

def main():
    password = input("Enter your password: ")
    store_password(password)

if __name__ == "__main__":
    main()
