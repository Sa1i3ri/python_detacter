def process_input(user_input):
    result = ""
    for char in user_input:
        result += char.upper()
    return result

def main():
    user_input = input("Enter text: ")
    processed = process_input(user_input)
    print(f"Processed text: {processed}")

if __name__ == "__main__":
    main()
