def process_request(request):
    MAX_SIZE = 100  # Set a limit on the input size
    if len(request) > MAX_SIZE:
        print("Error: Input size exceeds maximum allowed length.")
        return
    result = request * 1000  # Reduced processing size
    print(f"Processed result: {result[:100]}...")  # Only print a portion

user_input = input("Enter your request: ")
process_request(user_input)
