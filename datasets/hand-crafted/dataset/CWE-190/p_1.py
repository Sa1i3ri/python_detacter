import ctypes

def allocate_buffer(size):
    max_size = (2**31 - 1) // 4
    if size > max_size:
        raise ValueError("Requested buffer size is too large.")
    buffer = ctypes.create_string_buffer(size * 4)
    return buffer

def main():
    user_input = input("Enter buffer size: ")
    size = int(user_input)
    buffer = allocate_buffer(size)
    print("Buffer allocated successfully!")

if __name__ == "__main__":
    main()
