def read_file_at_offset(file_path, offset, size):
    max_offset = 2**31 - 1
    if offset < 0 or offset > max_offset:
        raise ValueError("Invalid offset value.")
    if size < 0 or size > max_offset:
        raise ValueError("Invalid size value.")
    with open(file_path, "rb") as file:
        file.seek(offset)
        data = file.read(size)
        return data

def main():
    file_path = input("Enter file path: ")
    offset = int(input("Enter offset: "))
    size = int(input("Enter size: "))
    data = read_file_at_offset(file_path, offset, size)
    print(f"Read {len(data)} bytes from file.")

if __name__ == "__main__":
    main()
