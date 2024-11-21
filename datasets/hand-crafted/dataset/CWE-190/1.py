import ctypes

def allocate_buffer(size):

    buffer = ctypes.create_string_buffer(size * 4)
    return buffer

def main():
    user_input = input("Enter buffer size: ")
    size = int(user_input)
    buffer = allocate_buffer(size)
    print("Buffer allocated successfully!")

if __name__ == "__main__":
    main()
