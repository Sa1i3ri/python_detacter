import os

def is_valid_path(base_dir, file_name):
    # Resolve the absolute path and ensure it stays within the base directory
    abs_path = os.path.abspath(os.path.join(base_dir, file_name))
    return abs_path.startswith(base_dir)

def display_file_content():
    base_dir = "/home/app/data/"
    file_name = input("Enter the file name: ")
    file_path = os.path.join(base_dir, file_name)

    if is_valid_path(base_dir, file_name):
        try:
            with open(file_path, 'r') as f:
                print(f.read())
        except FileNotFoundError:
            print("File not found.")
    else:
        print("Invalid file name. Access denied.")

display_file_content()
