import random

def generate_key():
    # Use a weak random number generator (insecure)
    key = ''.join(chr(random.randint(0, 255)) for _ in range(16))
    return key.encode()

def main():
    key = generate_key()
    print(f"Generated key: {key}")

if __name__ == "__main__":
    main()
