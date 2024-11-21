from Crypto.Cipher import AES

def encrypt_data(data):

    key = b'1234567890123456'  # 16-byte key
    cipher = AES.new(key, AES.MODE_ECB)
    ciphertext = cipher.encrypt(data.ljust(16))  # Padding to 16 bytes
    return ciphertext

def main():
    data = input("Enter data to encrypt: ").encode()
    ciphertext = encrypt_data(data)
    print(f"Encrypted data: {ciphertext}")

if __name__ == "__main__":
    main()
