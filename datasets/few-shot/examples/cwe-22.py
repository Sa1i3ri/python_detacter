import os

def display_file_content():
    base_dir = "/home/app/data/"
    file_name = input("Enter the file name: ")  # No validation for path traversal
    file_path = os.path.join(base_dir, file_name)

    with open(file_path, 'r') as f:
        print(f.read())

display_file_content()
