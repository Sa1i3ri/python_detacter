from Crypto.Cipher import AES
from Crypto.Random import get_random_bytes

def encrypt_data(data):
    key = get_random_bytes(16)
    cipher = AES.new(key, AES.MODE_GCM)
    nonce = cipher.nonce
    ciphertext, tag = cipher.encrypt_and_digest(data)
    return nonce, ciphertext, tag

def main():
    data = input("Enter data to encrypt: ").encode()
    nonce, ciphertext, tag = encrypt_data(data)
    print(f"Encrypted data: {ciphertext}")
    print(f"Nonce: {nonce}")
    print(f"Tag: {tag}")

if __name__ == "__main__":
    main()
