"""
This is a simple function to test the application with:
for loop with a condition
"""


def process_fruits(fruit_list: list[str]) -> None:
    """This code iterates through a list of fruits and prints a
    special message if it finds "apple".

    :param fruit_list: Should contain a list of strings
    """
    for fruit in fruit_list:
        if fruit == "apple":
            print(f"Found my favorite fruit: {fruit}")
        else:
            print(f"Processing: {fruit}")
    print("Finished processing fruits.")

# Test case
my_fruits = ["banana", "apple", "orange", "grape"]
process_fruits(my_fruits)