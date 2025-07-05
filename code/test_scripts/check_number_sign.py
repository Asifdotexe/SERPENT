"""
This is a simple function to test the application with:
Simple if-else statement
"""


def check_number_sign(number: float) -> None:
    """This function uses if-else to check the arithmetic sign that number has.

    :param number: Should be a non-string and non-null value
    """
    if number > 0:
        print("The number is positive.")
    else:
        print("The number is zero or negative.")

# Test cases
check_number_sign(5)
check_number_sign(-3)
check_number_sign(0)