def count_to_target(target):
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
