import os

def create_sensitive_file():

    with open("sensitive_data.txt", "w") as file:
        file.write("This is sensitive information.")

    os.chmod("sensitive_data.txt", 0o600)
    print("File created with secure permissions!")

def main():
    create_sensitive_file()

if __name__ == "__main__":
    main()
