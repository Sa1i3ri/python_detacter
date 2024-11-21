def process_request(request):
    # Vulnerable: No limit on input size
    result = request * 1000000  # Unchecked multiplication
    print(f"Processed result: {result[:100]}...")  # Only print a portion

user_input = input("Enter your request: ")
process_request(user_input)
