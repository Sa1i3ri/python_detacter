def calculate_area(width, height):
    # Vulnerable code: No check for overflow
    area = width * height
    print(f"The area is: {area}")

width = int(input("Enter width: "))
height = int(input("Enter height: "))
calculate_area(width, height)
