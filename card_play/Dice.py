"""
This module provides the Dice class
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
            sys.stderr.write("ERROR - " +
                             "non-string dice expression: " +
                             str(type(formula)) + "\n")
            return

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
            sys.stderr.write("ERROR - " +
                             "unrecognized dice expression: " +
                             formula + "\n")
            return

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
                sys.stderr.write("ERROR - " +
                                 "non-numeric value in dice-expression: " +
                                 formula + "\n")
        else:
            try:
                self.min_value = int(values[0])
                self.max_value = int(values[1])
                if self.min_value >= self.max_value:
                    self.min_value = None
                    self.max_value = None
                    sys.stderr.write("ERROR - " +
                                     "illegal range in dice expression: " +
                                     formula + "\n")
            except ValueError:
                sys.stderr.write("ERROR - " +
                                 "non-numeric value in range-expression: " +
                                 formula + "\n")

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


# pylint: disable=superfluous-parens; For consistency, I always use print()
def main():
    """
    test cases:
    """
    rolls = 20

    # test valid dice expressions
    dice = Dice("3D4")
    print("Rolling (3D4) " + str(dice.num_dice) + "D" + str(dice.dice_type) +
          " + " + str(dice.plus))
    for _ in range(rolls):
        print("\t{}".format(dice.roll()))
    print

    dice = Dice("d20")
    print("Rolling (d20) " + str(dice.num_dice) + "D" + str(dice.dice_type) +
          " + " + str(dice.plus))
    for _ in range(rolls):
        print("\t{}".format(dice.roll()))
    print

    dice = Dice("D%")
    print("Rolling (D%) " + str(dice.num_dice) + "D" + str(dice.dice_type) +
          " + " + str(dice.plus))
    for _ in range(rolls):
        print("\t{}".format(dice.roll()))
    print

    dice = Dice("2D2+3")
    print("Rolling (2D2+3) " + str(dice.num_dice) + "D" + str(dice.dice_type) +
          " + " + str(dice.plus))
    for _ in range(rolls):
        print("\t{}".format(dice.roll()))
    print

    # test a valid range expression
    dice = Dice("3-9")
    print("Rolling (3-9) " + str(dice.min_value) + "-" + str(dice.max_value))
    for _ in range(rolls):
        print("\t{}".format(dice.roll()))
    print

    # dest a fixed damage expression
    dice = Dice("47")
    print("Rolling (47) " + str(dice.plus))
    for _ in range(rolls):
        print("\t{}".format(dice.roll()))
    print

    # test invalid expressions
    _ = Dice("2D")
    _ = Dice("D")
    _ = Dice("xDy")

    _ = Dice("4-2")
    _ = Dice("-")
    _ = Dice("3-")
    _ = Dice("-3")
    _ = Dice("x-y")

    _ = Dice("100")
    _ = Dice("7to9")
    _ = Dice(100)


if __name__ == "__main__":
    main()
