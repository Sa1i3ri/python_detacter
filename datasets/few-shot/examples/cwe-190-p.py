import sys

def calculate_area(width, height):
    # Check for overflow
    if width > sys.maxsize // height:
        print("Error: Integer overflow detected.")
        return
    area = width * height
    print(f"The area is: {area}")

width = int(input("Enter width: "))
height = int(input("Enter height: "))
calculate_area(width, height)
