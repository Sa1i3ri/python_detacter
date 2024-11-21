from hashlib import md5

def store_password(password):
    # Vulnerable: MD5 is considered broken and insecure
    hashed_password = md5(password.encode()).hexdigest()
    print(f"Storing hashed password: {hashed_password}")
    return hashed_password

password = input("Enter your password: ")
store_password(password)
