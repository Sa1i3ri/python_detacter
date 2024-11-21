import os

def create_file():
    # Vulnerable: File is created with default permissions
    with open("sensitive_data.txt", "w") as f:
        f.write("This is sensitive information.")
    print("File created: sensitive_data.txt")

create_file()
os.system("ls -l sensitive_data.txt")  # Show permissions
