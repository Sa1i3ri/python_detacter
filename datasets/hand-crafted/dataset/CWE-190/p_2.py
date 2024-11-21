def count_to_target(target):
    max_int = 2**31 - 1
    if target > max_int:
        raise ValueError("Target value is too large.")
    count = 0
    while count <= target:
        count += 1
    print("Counting finished!")

def main():
    user_input = input("Enter target value: ")
    target = int(user_input)
    count_to_target(target)

if __name__ == "__main__":
    main()
