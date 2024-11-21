def is_valid_age(age):
    return 0 < age < 150

def process_age():
    try:
        age = int(input("Enter your age: "))
        if is_valid_age(age):
            print(f"Valid age: {age}")
        else:
            print("Invalid age entered.")
    except ValueError:
        print("Invalid input. Please enter a number.")

process_age()
