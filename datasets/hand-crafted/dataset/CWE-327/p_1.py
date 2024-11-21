from argon2 import PasswordHasher

def store_password(password):

    ph = PasswordHasher()
    hashed_password = ph.hash(password)
    print(f"Stored password hash: {hashed_password}")

def main():
    password = input("Enter your password: ")
    store_password(password)

if __name__ == "__main__":
    main()
