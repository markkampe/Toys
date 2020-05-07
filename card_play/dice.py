"""
This module provides the Dice class (formula based random numbers)
"""
import sys
from random import randint


# pylint: disable=too-few-public-methods
class Dice(object):
    """
    This class implements formulae and rolls against them
    """

    # pylint: disable=too-many-branches
    def __init__(self, formula):
        """
        @param formula: description of roll, expressed as ...
            * dice (e.g. "D100", "3D6+2" or "D%")
            * a range of inclusive values (e.g. "3-18")
            * a simple number (e.g. "14")
        """
        self.num_dice = None
        self.dice_type = None
        self.min_value = None
        self.max_value = None
        self.plus = 0

        # make sure it is a string
        if not isinstance(formula, str):
            raise ValueError("non-string dice expression")

        # figure out what kind of expression this is
        delimiter = None
        if 'D' in formula:
            delimiter = 'D'
            values = formula.split(delimiter)
        elif 'd' in formula:
            delimiter = 'd'
            values = formula.split(delimiter)
        elif '-' in formula:
            delimiter = '-'
            values = formula.split(delimiter)
        elif formula.isnumeric():
            self.plus = int(formula)
            return

        # see if it has known form and 2 values
        if delimiter is None or len(values) != 2:
            raise ValueError("unrecognized dice expression")

        # process the values
        if delimiter == 'D' or delimiter == 'd':
            try:
                self.num_dice = 1 if values[0] == '' else int(values[0])

                # there might be a plus after the dice type
                if '+' in values[1]:
                    parts = values[1].split('+')
                    values[1] = parts[0]
                    values.append(parts[1])
                else:
                    values.append('0')

                self.dice_type = 100 if values[1] == '%' else int(values[1])
                self.plus = int(values[2])
            except ValueError:
                raise ValueError("non-numeric value in dice expression")
        else:
            try:
                self.min_value = int(values[0])
                self.max_value = int(values[1])
                if self.min_value >= self.max_value:
                    self.min_value = None
                    self.max_value = None
                    raise ValueError("illegal range in dice expression")
            except ValueError:
                raise ValueError("non-numeric value in dice expression")

    def str(self):
        """
        return string representation of these dice"
        """
        if self.num_dice is not None and self.dice_type is not None:
            descr = "{}D{}".format(self.num_dice, self.dice_type)
            if self.plus > 0:
                descr += "+{}".format(self.plus)
        elif self.min_value is not None and self.max_value is not None:
            descr = "{}-{}".format(self.min_value, self.max_value)
        elif self.plus > 0:
            descr = str(self.plus)
        else:
            descr = ""

        return descr

    def roll(self):
        """
        roll this set of dice
        """
        total = 0

        if self.num_dice is not None and self.dice_type is not None:
            for _ in range(self.num_dice):
                total += randint(1, self.dice_type)
        elif self.min_value is not None and self.max_value is not None:
            total = randint(self.min_value, self.max_value)

        return total + self.plus


# pylint: disable=superfluous-parens; for consistency I always use print()
def test(formula, min_expected, max_expected, rolls=20):
    """
    test that a formula generates rolls w/expected values
    @param formula: (string) for the DIce
    @param min_expected: minimum expected value
    @param max_expected: maximum expecetd value
    @param rolls: number of test rolls
    """
    dice = Dice(formula)
    min_rolled = 666666
    max_rolled = -666666
    for _ in range(rolls):
        rolled = dice.roll()
        if rolled < min_rolled:
            min_rolled = rolled
        if rolled > max_rolled:
            max_rolled = rolled

    print("    legal formula {} ({}): returns {} values between {} and {}".
          format(formula, dice.str(), rolls, min_rolled, max_rolled))

    assert min_rolled >= min_expected, "roll returns below-minimum values"
    assert max_rolled <= max_expected, "roll returns above-maximum values"

    return min_rolled >= min_expected and max_rolled <= max_expected


def main():
    """
    test cases:
    """

    # test valid dice expressions
    tests_run = 0
    tests_passed = 0

    tests_run += 1
    if test("3D4", 3, 12, 40):
        tests_passed += 1

    tests_run += 1
    if test("d20", 1, 20, 80):
        tests_passed += 1

    tests_run += 1
    if test("D%", 1, 100, 300):
        tests_passed += 1

    tests_run += 1
    if test("2D2+3", 5, 7):
        tests_passed += 1

    tests_run += 1
    if test("3-9", 3, 9):
        tests_passed += 1

    tests_run += 1
    if test("47", 47, 47, 10):
        tests_passed += 1

    # test detection of invalid expressions
    for formula in ["2D", "D", "xDy",
                    "4-2", "-", "3-", "x-y",
                    "7to9", 100]:
        tests_run += 1
        try:
            dice = Dice(formula)
            sys.stderr.write("    ERROR: illegal formula {} accepted as {}\n".
                             format(formula, dice.str()))
        except ValueError:
            print("  illegal formula {}: {}".
                  format(formula, sys.exc_info()[1]))
            tests_passed += 1

    print("{}/{} Dice test casees passed\n".format(tests_passed, tests_run))


if __name__ == "__main__":
    main()
