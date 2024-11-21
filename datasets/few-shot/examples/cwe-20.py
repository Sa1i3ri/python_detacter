def process_age():
    age = int(input("Enter your age: "))  # No input validation
    if age > 0 and age < 150:
        print(f"Valid age: {age}")
    else:
        print("Invalid age entered.")

process_age()
