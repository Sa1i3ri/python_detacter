import hashlib
import os

def store_password(password):
    # Secure: Use a strong hashing algorithm with a salt
    salt = os.urandom(16)  # Generate a random 16-byte salt
    hashed_password = hashlib.pbkdf2_hmac('sha256', password.encode(), salt, 100000)
    print(f"Storing hashed password: {salt.hex()}:{hashed_password.hex()}")
    return salt, hashed_password

password = input("Enter your password: ")
store_password(password)
