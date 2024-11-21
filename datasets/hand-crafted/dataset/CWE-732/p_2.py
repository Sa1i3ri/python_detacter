import os

def create_upload_directory():
    upload_dir = "/tmp/uploads"
    os.makedirs(upload_dir, mode=0o700, exist_ok=True)
    print(f"Upload directory created with secure permissions at {upload_dir}")

def main():
    create_upload_directory()

if __name__ == "__main__":
    main()
