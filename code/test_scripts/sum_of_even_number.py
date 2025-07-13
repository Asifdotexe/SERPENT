"""
This is a simple function to test the application with:
Calculating Sum of Even Numbers
"""

def sum_even_numbers(start: int, end: int) -> None:
    """This function calculates the sum of all even numbers within a given range.

    :param start: Numerical non-null element to indicate the starting value
    :param end: Numerical non-null element to indicate the ending value
    :return: None
    """
    total_sum = 0
    for num in range(start, end + 1):
        if num % 2 == 0:
            total_sum += num
    return total_sum

# Test case
result = sum_even_numbers(1, 10)
print(f"The sum of even numbers from 1 to 10 is: {result}")