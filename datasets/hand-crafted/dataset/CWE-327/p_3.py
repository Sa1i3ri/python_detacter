from secrets import token_bytes

def generate_key():
    key = token_bytes(16)
    return key

def main():
    key = generate_key()
    print(f"Generated key: {key}")

if __name__ == "__main__":
    main()
