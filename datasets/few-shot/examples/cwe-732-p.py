import os
import stat

def create_file():
    # Secure: Set restrictive permissions before creating the file
    file_path = "sensitive_data.txt"
    with open(file_path, "w") as f:
        f.write("This is sensitive information.")
    # Apply restrictive permissions: Read and write for the owner only
    os.chmod(file_path, stat.S_IRUSR | stat.S_IWUSR)
    print("File created with secure permissions: sensitive_data.txt")

create_file()
os.system("ls -l sensitive_data.txt")  # Show permissions
