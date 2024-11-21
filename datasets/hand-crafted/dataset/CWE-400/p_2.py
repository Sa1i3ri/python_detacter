def process_input(user_input):
    MAX_INPUT_SIZE = 1024
    if len(user_input) > MAX_INPUT_SIZE:
        raise ValueError("Input size exceeds allowed limit.")
    result = ""
    for char in user_input:
        result += char.upper()
    return result

def main():
    user_input = input("Enter text (max 1024 characters): ")
    try:
        processed = process_input(user_input)
        print(f"Processed text: {processed}")
    except ValueError as e:
        print(e)

if __name__ == "__main__":
    main()
