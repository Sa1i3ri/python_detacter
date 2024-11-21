import os

def create_sensitive_file():
    with open("sensitive_data.txt", "w") as file:
        file.write("This is sensitive information.")
    print("File created successfully!")

def main():
    create_sensitive_file()

if __name__ == "__main__":
    main()
