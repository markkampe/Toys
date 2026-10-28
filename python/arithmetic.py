#!/usr/bin/python3
"""
 methods for elementary school arithmetic tutoring
   perform basic arithmetic operations, showing all the steps:
       carries, borrows, partial products, long division
"""


def addition_with_carries(addend_1, addend_2):
    """
    add two integers, showing the carries
    : param (int) addend_1
    : param (int) addend_2
    """
    # Convert inputs to strings to handle digit-by-digit operations
    str1 = str(addend_1)
    str2 = str(addend_2)

    # Pad strings with leading zeros to make them equal length
    max_len = max(len(str1), len(str2))
    str1 = str1.zfill(max_len)
    str2 = str2.zfill(max_len)

    carries = [0] * (max_len + 1)
    current_carry = 0

    # Calculate carries from right to left
    for i in range(max_len - 1, -1, -1):
        digit1 = int(str1[i])
        digit2 = int(str2[i])

        total = digit1 + digit2 + current_carry
        current_carry = total // 10
        carries[i] = current_carry  # Store carry for the next column to left

    # Format the carry line (shift left by 1 position visually)
    # If the carry is 0, we print a space; otherwise, print the carry digit
    carry_line = "".join(str(c) if c > 0 else " " for c in carries[1:])
    if carries[0] > 0:
        carry_line = str(carries[0]) + carry_line
    else:
        carry_line = " " + carry_line

    # Calculate final result
    result = addend_1 + addend_2

    # Determine the width needed for clean right-alignment
    width = max(max_len + 2, len(str(result)) + 2)

    # Print the formatted output
    print(f"Carries:  {carry_line.rjust(width)}")
    print(f"          {str(addend_1).rjust(width)}")
    print(f"        + {str(addend_2).rjust(width)}")
    print(f"          {'-' * width}")
    print(f"Result:   {str(result).rjust(width)}")

    return result


# pylint: disable=too-many-locals
def subtraction_with_borrows(minuend, subtrahend):
    """
    subtract one integer from another, showing the borrows
    : parm (int) minuend: number being subtracted from
    : parm (int) subtrahend: number being subtracted
    """
    if subtrahend > minuend:
        print("This script is optimized for positive results (Num1 >= Num2).")
        return

    # Convert to strings and pad with leading zeros
    str1, str2 = str(minuend), str(subtrahend)
    max_len = max(len(str1), len(str2))
    str1 = str1.zfill(max_len)
    str2 = str2.zfill(max_len)

    # Convert to mutable lists of digits for processing borrows
    digits1 = [int(d) for d in str1]
    digits2 = [int(d) for d in str2]

    borrows = [" "] * max_len
    slashes = [" "] * max_len
    new_digits = [" "] * max_len

    # Loop from right to left
    for i in range(max_len - 1, -1, -1):
        if digits1[i] < digits2[i]:
            # Find the next available non-zero digit to borrow from
            borrow_idx = i - 1
            while borrow_idx >= 0 and digits1[borrow_idx] == 0:
                borrow_idx -= 1

            # Cascade the borrow down through any zeros
            for j in range(borrow_idx, i):
                slashes[j] = "/"
                if digits1[j] == 0:
                    new_digits[j] = "9"
                    digits1[j] = 9
                else:
                    new_digits[j] = str(digits1[j] - 1)
                    digits1[j] -= 1

            # Apply the borrow to the current column
            borrows[i] = "1"
            digits1[i] += 10

    # Format lines for printing
    width = max_len + 4
    borrow_line = "".join(borrows).rjust(width)
    slash_line = "".join(slashes).rjust(width)
    new_dig_line = "".join(new_digits).rjust(width)

    print(f"Borrows:  {borrow_line}")
    print(f"          {new_dig_line}")
    print(f"          {slash_line}")
    print(f"          {str(minuend).rjust(max_len).rjust(width)}")
    print(f"        - {str(subtrahend).rjust(max_len).rjust(width)}")
    print(f"          {'-' * max_len}")
    print(f"Result:   {str(minuend - subtrahend).rjust(max_len).rjust(width)}")

    return minuend - subtrahend


def multiply_with_partial_products(multiplier, multiplicand):
    """
    multiply two numbers, showing the partial products
    : parm (int) multiplier
    : parm (int) multiplicand
    """
    # Convert inputs to strings to handle formatting and digit iteration
    str1 = str(multiplier)
    str2 = str(multiplicand)

    # Calculate the maximum width needed for clean alignment
    max_len = len(str(multiplier * multiplicand)) + 2

    # Print the setup
    print(f"{str1:>{max_len}}")
    print(f"x{str2:>{max_len-1}}")
    print("-" * max_len)

    # Iterate through digits of the second number from right to left
    for i, digit in enumerate(reversed(str2)):
        digit_val = int(digit)
        # Calculate the partial product for this step
        partial = multiplier * digit_val

        # Format output line w/trailing spaces to represent place value shifts
        if partial == 0 and i > 0:
            # Handle zeros gracefully
            line = "0" + " " * i
        else:
            line = f"{partial}" + " " * i

        print(f"{line:>{max_len}}")

    # Print the final result line
    print("-" * max_len)
    print(f"{multiplier * multiplicand:>{max_len}}")

    return multiplier * multiplicand


def long_division(dividend: int, divisor: int):
    """
    perform a division operation, showing intermediate subtractions
    : parm (int) dividend: number to be divided
    : parm (int) divisor: number to divide by
    """
    if divisor == 0:
        raise ValueError("Cannot divide by zero.")

    # Handle negative numbers for the final result sign
    is_negative = (dividend < 0) ^ (divisor < 0)
    dividend, divisor = abs(dividend), abs(divisor)

    dividend_str = str(dividend)
    quotient_str = ""
    current_buffer = 0
    steps = []

    print(f"Dividing {dividend} by {divisor}:\n")

    # Process the dividend digit by digit
    for i, digit in enumerate(dividend_str):
        # 1. Bring down the next digit
        current_buffer = current_buffer * 10 + int(digit)
        step_info = {"step": i + 1, "brought_down": current_buffer}

        # 2. Determine how many times the divisor goes into the current buffer
        current_quotient_digit = current_buffer // divisor
        quotient_str += str(current_quotient_digit)

        # 3. Calculate product and new intermediate remainder
        product = current_quotient_digit * divisor
        remainder = current_buffer - product

        step_info.update({
            "digit_placed": current_quotient_digit,
            "product": product,
            "remainder": remainder
        })
        steps.append(step_info)

        # Print the formatted step
        print(f"Step {i+1}:")
        print(f"  Current working value: {current_buffer}")
        print(f"  {current_buffer} // {divisor} = {current_quotient_digit}")
        print(f"  Multiply: {current_quotient_digit} * {divisor} = {product}")
        print(f"  Subtract: {current_buffer} - {product} = {remainder}")
        print("  Current accumulated quotient: " +
              f"{quotient_str.lstrip('0') or '0'}\n")

        # The remainder becomes the base for the next iteration
        current_buffer = remainder

    # Final cleanup of results
    final_quotient = int(quotient_str)
    if is_negative and final_quotient != 0:
        final_quotient = -final_quotient

    print("-" * 30)
    print(f"Final Quotient : {final_quotient}")
    print(f"Final Remainder: {current_buffer}")

    return final_quotient, current_buffer, steps


#
# usage examples
#
if __name__ == '__main__':
    print("EXAMPLE: addition with carries\n")
    addition_with_carries(789, 456)
    print("====================\n")

    print("\nEXAMPLE: subtraction with borrows\n")
    subtraction_with_borrows(1002, 456)

    print("====================\n")
    print("\nEXAMPLE: multiplication with partial products\n")
    multiply_with_partial_products(123, 45)

    print("====================\n")
    print("\nEXAMPLE: long division\n")
    _quotient, _remainder, _intermediate_steps = long_division(4812, 12)
