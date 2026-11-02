#!/usr/bin/python3
"""
    Tutoring arithmetic involves the ability to check
    carries, borrows, partial products, and long-division.
    I could do each problem myself, but this is time-consuming
    (slows the students down) and requires that I write very
    carefully.  I decided it would be much better if I just
    wrote a program to do these things (showing all steps).

    I did a google search for pedagogical arithmetic
      and Google AI gave me python that kind-of-worked
      for integers.  I used this as a starting point,
      did some refactoring, enhanced them to support
      decimal quantities, and improve the readability
      of the multiplication and long-division output.
"""


#
# utility routies to facilitate working with decimal fractions
#
def times_ten(number: str, power=1):
    """
    multiplication by a power of ten for numeric strings

        done with numeric strings to avoid the inevitable
        errors from floating point multiplication of binary
        (vs decimal) numbers.

    parm: number to be multiplied (string)
    parm: power of ten (int)
    Return:
        string representing the desired product
    """
    for _i in range(power):
        dp = number.find('.')
        if dp < 0:          # integers are trivial
            number += '0'
            continue

        # it depends where the decimal point is
        tot_len = len(number)
        if dp == 1 and number[0] == '0':    # 0.xxxx
            if tot_len == 3:                # 0.x -> x
                number = number[2]
            else:                           # 0.xyz -> x.yz
                number = number[2] + '.' + number[3:]
        elif dp == tot_len - 2:             # xy.z -> xyz
            number = number[:dp] + number[dp+1]
        else:                               # x.yz -> xy.z
            number = number[:dp] + number[dp+1] + '.' + number[dp+2:]
    return number


def divby_ten(number: str, power=1):
    """
    division by a power of ten for numeric strings

        done with numeric strings to avoid the inevitable
        errors from floating point division of binary
        (vs decimal) numbers.

    parm: number to be divided (string)
    parm: power of ten (int)
    Return:
        string representing the desired product
    """
    for _i in range(power):
        dp = number.find('.')
        tot_len = len(number)
        if dp < 0:
            if tot_len == 1:                # x -> 0.x
                number = "0." + number
            else:                           # xy -> x.y
                number = number[:-1] + '.' + number[-1]
        elif dp == 1 and number[0] != '0':  # x.yz -> 0.xyz
            number = "0." + number[0] + number[2:]
        elif dp == 1 and number[0] == '0':  # 0.xyz = 0.0xyz
            number = number[:2] + '0' + number[2:]
        else:                               # xy.z -> x.yz
            number = number[:dp-1] + '.' + number[dp-1] + number[dp+1:]
    return number


def decimal_places(string: str) -> int:
    """
    number of digits to the right of the decimal point
    """
    # see where the decimal point is
    dot = string.find('.')
    if dot <= 0:
        return 0
    return len(string) - (dot + 1)


def decimal_align(num1: str, num2: str) -> (str, str):
    """
    ensure two (numeric) strings have same number of digits after decimal

    Return:
        two numeric strings with equal decimal precision

    Note:
        this is required for addition and subtraction,
        but is wrong for division, where we want to
        to turn the divisor into an integer, but don't
        care about the precision of the dividend.
    """
    # see if either number has a decimal fraction
    scale1 = decimal_places(num1)
    scale2 = decimal_places(num2)

    # if two integers, they are fine as given
    if scale1 == 0 and scale2 == 0:
        return num1, num2

    # if they are different, zero-pad the shorter
    if scale1 > scale2:
        if scale2 == 0:
            num2 += '.'
        num2 += '0' * (scale1 - scale2)
    elif scale2 > scale1:
        if scale1 == 0:
            num1 += '.'
        num1 += '0' * (scale2 - scale1)

    return num1, num2


def no_leading_zeroes(value: str) -> str:
    """ strip leading zeroes off of a number """

    # string is only zero
    stripped = value.lstrip()
    if stripped == '0':
        return value

    # first non-blank is not zero
    if stripped[0] != '0':
        return value

    # copy the string, skipping any leading zeroes
    newstr = ""
    length = len(value)
    got_stuff = False
    for i in range(length):
        # are we still in leading whitespace?
        if value[i] == ' ':
            newstr += ' '
        # we are past any leading zeroes
        elif got_stuff or value[i] != '0':
            got_stuff = True
            newstr += value[i]
        # is this a zero before a decimal point
        elif i < length - 1 and value[i+1] == '.':
            got_stuff = True
            newstr += value[i]
        # this is a leading zero
        else:
            newstr += ' '
    return newstr


class Arithmetic:
    """
        basic arithmetic operations, showing all the steps:
           addition/subtraction: carries & borrows,
           multiplication: partial products
           long division: each product/subtraction
           exponentiation with all the multiplies
    """
    debug = False

    # pylint: disable=too-many-locals
    def addition_with_carries(self, addend_1: str, addend_2: str) -> int/float:
        """
        add two numbers, showing the total and carries
        output: carries
                addend 1
                addend 2
                --------
                sum
        """
        # Convert inputs to strings to handle digit-by-digit operations
        str1, str2 = decimal_align(addend_1, addend_2)

        # Pad strings with leading blanks to make them equal length
        max_len = max(len(str1), len(str2)) + 1
        str1 = str1.rjust(max_len)
        str2 = str2.rjust(max_len)

        # Calculate carries from right to left
        carries = [0] * max_len
        current_carry = 0
        result_s = ""
        for i in range(max_len - 1, -1, -1):
            if str1[i] == '.':
                result_s = '.' + result_s
                carries[i] = 0
                continue

            carries[i] = current_carry  # did I have a carry-in?
            digit1 = 0 if str1[i] == ' ' else int(str1[i])
            digit2 = 0 if str2[i] == ' ' else int(str2[i])
            total = digit1 + digit2 + current_carry
            result_s = str(total % 10) + result_s
            current_carry = total // 10

        # If the carry is 0, we print a space; otherwise, print the carry digit
        carry_line = "".join(str(c) if c > 0 else " " for c in carries)

        # check our result
        result_s = no_leading_zeroes(result_s)
        result = float(result_s)
        correct = float(addend_1) + float(addend_2)
        if correct == result:
            vs_corr = ""
        else:
            vs_corr = f" (vs {correct})"

        # Determine the width needed for clean right-alignment
        width = max(max_len + 2, len(result_s) + 2)

        # Print the formatted output
        print(f"Carries:  {carry_line.rjust(width)}")
        print(f"          {str1.rjust(width)}")
        print(f"        + {str2.rjust(width)}")
        print(f"          {'-' * width}")
        print(f"Sum:      {result_s.rjust(width)}{vs_corr}")

        return result

    # pylint: disable=too-many-locals,too-many-branches,too-many-statements
    def subtraction_with_borrows(self, minuend, subtrahend):
        """
        subtract one integer from another, showing the borrows
          parm (str) minuend: number being subtracted from
          parm (str) subtrahend: number being subtracted

          output:   additions from borrows
                    reductions from values
                    columns from which there have been borrows
                    minuend
                    subtrahend
                    -------
                    diference
        """
        # Convert to strings and pad with leading zeros
        str1, str2 = decimal_align(minuend, subtrahend)
        max_len = max(len(str1), len(str2))
        str1 = str1.rjust(max_len)
        str2 = str2.rjust(max_len)
        dp = decimal_places(str1)

        # borrowing algorithm assumes positive difference
        if dp == 0:
            correct = int(minuend) - int(subtrahend)
        else:
            correct = round(float(minuend) - float(subtrahend), dp)
        larger = str1 if correct >= 0 else str2
        smaller = str2 if correct >= 0 else str1

        # Convert to mutable lists of digits for processing borrows
        digits1 = [0] * max_len
        j = max_len - 1
        for i in range(max_len - 1, -1, -1):
            if larger[i] != ' ' and larger[i] != '.':
                digits1[j] = int(larger[i])
                j -= 1
        digits2 = [0] * max_len
        j = max_len - 1
        for i in range(max_len - 1, -1, -1):
            if smaller[i] != ' ' and smaller[i] != '.':
                digits2[j] = int(smaller[i])
                j -= 1

        borrows = [" "] * max_len       # borrowed for this place
        slashes = [" "] * max_len       # borrowed from this place
        new_digits = [" "] * max_len    # reduced digit in this place
        rslt_str = ""                   # accumulated difference

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
            rslt_str = str(digits1[i] - digits2[i]) + rslt_str

        # Format output lines for printing
        width = max_len + 4
        index = max_len - dp
        borrow_line = "".join(borrows[:index])
        slash_line = "".join(slashes[:index])
        new_dig_line = "".join(new_digits[:index])
        rslt_line = "".join(rslt_str[:index])
        if dp > 0:      # re-insert (space for) decimal points
            borrow_line += ' ' + "".join(borrows[index:])
            slash_line += ' ' + "".join(slashes[index:])
            new_dig_line += '.' + "".join(new_digits[index:])
            rslt_line += '.' + "".join(rslt_str[index:])
        rslt_line = no_leading_zeroes(rslt_line)

        # check our answer vs the correct one
        result = float(rslt_line)
        if result == correct:
            vs_corr = ""
        else:
            vs_corr = f" (vs {correct})"

        # figure out what signts to put on the minuend and subtrahend
        sl = ' ' if correct >= 0 else '-'
        ss = '-' if correct >= 0 else '+'

        print(f"Borrows:  {borrow_line.rjust(width)}")
        print(f"          {new_dig_line.rjust(width)}")
        print(f"          {slash_line.rjust(width)}")
        print(f"        {sl} {larger.rjust(width)}")
        print(f"        {ss} {smaller.rjust(width)}")
        print(f"          {('-' * max_len).rjust(width)}")
        print(f"Diff:     {rslt_line.rjust(width)}{vs_corr}")

        return result

    def multiply_with_partial_products(self, multiplier, multiplicand):
        """
        multiply two numbers, showing the partial products
        : parm (int) multiplier
        : parm (int) multiplicand
        output: multiplicand
                multiplier
                ----------
                partial sums (without decimals)
                ----------
                product

        """
        # Convert inputs to strings to handle formatting and digit iteration
        str1 = multiplier
        str2 = multiplicand

        # Calculate the maximum width needed for clean alignment
        dp = decimal_places(str1) + decimal_places(str2)
        if dp == 0:
            m1 = int(multiplier)
            m2 = int(multiplicand)
        else:
            m1 = float(multiplier)
            m2 = float(multiplicand)
        correct = round(m1 * m2, dp)
        max_len = len(str(correct)) + 2

        # Print the setup
        print(f"{str2:>{max_len}}")
        print(f"x{str1:>{max_len-1}}")
        print("-" * max_len)

        # scale multiplier/multiplicand into integers for computation
        str1 = times_ten(str1, decimal_places(str1))
        m2 = int(times_ten(str2, decimal_places(str2)))

        # Iterate through digits of the multiplier from right to left
        calculated = 0
        for i, digit in enumerate(reversed(str1)):
            digit_val = int(digit)
            # Calculate the partial product for this step
            partial = m2 * digit_val

            # Format output w/trailing spaces to represent place value shifts
            if partial == 0 and i > 0:
                # Handle zeros gracefully
                line = "0" + " " * i
            else:
                line = f"{partial}" + " " * i

            # sum the partial products
            calculated += int(line) * (10**i)

            # decimal points to the partial products
            if i < dp:
                end = len(line)
                whole = line[:end-dp]
                fract = line[end-dp:]
                line = f"{whole}.{fract}".rjust(max_len)
            elif dp > 0 and i == dp:
                line = (line + ' ').rjust(max_len)
            else:
                line = line.rjust(max_len)
            print(line)

        # re-insert the decimal point in the calculated total
        calc_str = str(calculated)  # a correct integer
        if dp > 0:
            calc_str = divby_ten(calc_str, dp)
            calculated = float(calc_str)

        # check for correct answer
        if calculated == correct:
            vs_corr = ""
        else:
            vs_corr = f" (vs {correct})"

        # Print the final result line
        print("-" * max_len)
        print(f"{calc_str.rjust(max_len)} {vs_corr}")

        return calculated

    def long_division(self, dividend_str: str, divisor_str: str):
        """
        perform a division operation, showing intermediate subtractions
          parm dividend: number to be divided
          parm divisor: number to divide by

        returns [quotient, remainder]
        """
        # get numerical values for divisor and dividend
        dp_d = decimal_places(divisor_str)
        divisor = int(divisor_str) if dp_d == 0 else float(divisor_str)
        if divisor == 0:
            raise ValueError("Cannot divide by zero.")
        dp_n = decimal_places(dividend_str)
        dividend = int(dividend_str) if dp_d == 0 else float(dividend_str)

        # compute the correct answer
        correct = dividend/divisor

        # Handle negative numbers for the final result sign
        is_negative = (dividend < 0) ^ (divisor < 0)
        dividend, divisor = abs(dividend), abs(divisor)

        # general layout parameters
        denom_width = len(divisor_str)
        numer_width = len(dividend_str)
        extra_digits = 1 if dp_n > dp_d else 1 + dp_d - dp_n
        right_column = numer_width + 4

        # form for the division problem
        obleus = " ) "
        obleus_width = len(obleus)
        obleus_line = ' ' * (denom_width + 1) + \
                      '_' * (obleus_width + numer_width + extra_digits)

        div_str = dividend_str
        if dp_d > 0:        # rescale dividend for an integer divider
            divisor = int(times_ten(divisor_str, dp_d))
            div_str = times_ten(dividend_str, dp_d)
        if dp_d > dp_n:     # guess at how much precision we want
            if '.' not in div_str:
                div_str += '.'
            div_str += '0' * (dp_d - dp_n)
        if self.debug:  # the above took a lot of tuning
            print(f"DBG: rework to {div_str}/{divisor}" + f" = {correct}")

        # Process the dividend digit by digit
        quotient_str = ""
        current_buffer = 0
        indent = denom_width + obleus_width
        steps = []
        for i, digit in enumerate(div_str):
            # ignore decimal points in the dividend
            if digit == '.':
                quotient_str += '.'
                continue

            # figure out where our indentation should be
            cur_width = indent + i + 1

            # 1. Bring down the next digit
            if i > 0 and current_buffer == 0:
                current_buffer = int(digit)
                bringdown_str = ('0'+digit).rjust(cur_width)
            else:
                current_buffer = current_buffer * 10 + int(digit)
                bringdown_str = str(current_buffer).rjust(cur_width)

            # 2. how many times the divisor goes into the current buffer
            current_quotient_digit = current_buffer // divisor
            quotient_str += str(int(current_quotient_digit))

            # 3. Calculate product
            product = int(current_quotient_digit * divisor)
            if product > 0:
                product_str = str(-product).rjust(cur_width)
            else:
                product_str = "-0".rjust(cur_width)
            padding = ' ' * (right_column - i)
            product_str += f"{padding} ... "
            product_str += f"({current_quotient_digit} x {divisor})"

            # 4. calculate the new remainder
            dashes = ('-' * len(str(current_buffer))).rjust(cur_width)
            remainder = current_buffer - product
            remain_str = str(remainder).rjust(cur_width)

            # record these results
            step_info = (bringdown_str, product_str, dashes, remain_str)
            steps.append(step_info)

            # The remainder becomes the base for the next iteration
            current_buffer = remainder

        # Final cleanup of results
        quotient_str = no_leading_zeroes(quotient_str)
        final_quotient = float(quotient_str)
        if is_negative and final_quotient != 0:
            final_quotient = -final_quotient

        # check it for correctness
        dp = max(dp_d - dp_n, 0)
        if final_quotient == round(correct, dp):
            vs_corr = ""
        else:
            vs_corr = f" (vs {round(correct, dp+1)})"

        # print out the entire computation

        print(f"    {quotient_str.rjust(cur_width)}{vs_corr}")
        print(f"    {obleus_line}")
        print(f"    {divisor_str}{obleus}{dividend_str}")

        for (index, results) in enumerate(steps):
            print(f"    {results[0]}")  # bring-down
            print(f"    {results[1]}")  # digit * divisor
            print(f"    {results[2]}")  # dashes
            if index < len(steps) - 1:
                continue
            print(f"    {results[3]}{padding} ... remainder")

        return final_quotient, remainder

    def exponentiation(self, number, power):
        """
        raise a number to a specified (integer) power
        """
        p = int(power)
        n = float(number) if '.' in number else int(number)
        result = 1
        string = ""
        for i in range(p):
            result *= n
            if i != 0:
                string += " x "
            string += number

        if p == 0:
            print(f"    {result} ... (anything raised to the 0 power)")
        else:
            print(f"    {string} = {result}")
        return result

    def greatest_common_factor(self, num1, num2):
        """
        Greatest Common Factor
        """
        return f"GCF({num1}, {num2}"

    def least_common_multiple(self, num1, num2):
        """
        Least Common Multiple
        """
        return f"LCM({num1}, {num2}"
