import os

def create_upload_directory():

    upload_dir = "/tmp/uploads"
    os.makedirs(upload_dir, exist_ok=True)
    print(f"Upload directory created at {upload_dir}")

def main():
    create_upload_directory()

if __name__ == "__main__":
    main()
