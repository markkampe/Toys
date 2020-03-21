import sys
from random import randint


class Dice:
    """
    This class implements formulae and rolls against them
    """
    numDice = None
    diceType = None
    minValue = None
    maxValue = None
    plus = 0

    def __init__(self, formula):
        """
        @param (String): formula for the roll
            expressed as dice (e.g. "D100", "3D6+2" or "D%")
            or as range of inclusive values (e.g. "3-18")

        """
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
                self.numDice = 1 if values[0] == '' else int(values[0])

                # there might be a plus after the dice type
                if '+' in values[1]:
                    parts = values[1].split('+')
                    values[1] = parts[0]
                    values.append(parts[1])
                else:
                    values.append('0')

                self.diceType = 100 if values[1] == '%' else int(values[1])
                self.plus = int(values[2])
            except ValueError:
                sys.stderr.write("ERROR - " +
                                 "non-numeric value in dice-expression: " +
                                 formula + "\n")
        else:
            try:
                self.minValue = int(values[0])
                self.maxValue = int(values[1])
                if self.minValue >= self.maxValue:
                    self.minValue = None
                    self.maxValue = None
                    sys.stderr.write("ERROR - " +
                                     "illegal range in dice expression: " +
                                     formula + "\n")
            except ValueError:
                sys.stderr.write("ERROR - " +
                                 "non-numeric value in range-expression: " +
                                 formula + "\n")

    def roll(self):
        """
        """
        sum = 0

        if self.numDice is not None and self.diceType is not None:
            for times in range(self.numDice):
                sum += randint(1, self.diceType)
        elif self.minValue is not None and self.maxValue is not None:
            sum = randint(self.minValue, self.maxValue)

        return sum + self.plus


if __name__ == "__main__":
    """
    test cases:
    """
    rolls = 20

    # test valid dice expressions
    dice = Dice("3D4")
    print("Rolling (3D4) " + str(dice.numDice) + "D" + str(dice.diceType) +
          " + " + str(dice.plus))
    for i in range(rolls):
        print("\t{}".format(dice.roll()))
    print

    dice = Dice("d20")
    print("Rolling (d20) " + str(dice.numDice) + "D" + str(dice.diceType) +
          " + " + str(dice.plus))
    for i in range(rolls):
        print("\t{}".format(dice.roll()))
    print

    dice = Dice("D%")
    print("Rolling (D%) " + str(dice.numDice) + "D" + str(dice.diceType) +
          " + " + str(dice.plus))
    for i in range(rolls):
        print("\t{}".format(dice.roll()))
    print

    dice = Dice("2D2+3")
    print("Rolling (2D2+3) " + str(dice.numDice) + "D" + str(dice.diceType)
          + " + " + str(dice.plus))
    for i in range(rolls):
        print("\t{}".format(dice.roll()))
    print

    # test a valid range expression
    dice = Dice("3-9")
    print("Rolling (3-9) " + str(dice.minValue) + "-" + str(dice.maxValue))
    for i in range(rolls):
        print("\t{}".format(dice.roll()))
    print

    # dest a fixed damage expression
    dice = Dice("47")
    print("Rolling (47) " + str(dice.plus))
    for i in range(rolls):
        print("\t{}".format(dice.roll()))
    print

    # test invalid expressions
    bad = Dice("2D")
    bad = Dice("D")
    bad = Dice("xDy")

    bad = Dice("4-2")
    bad = Dice("-")
    bad = Dice("3-")
    bad = Dice("-3")
    bad = Dice("x-y")

    bad = Dice("100")
    bad = Dice("7to9")
    bad = Dice(100)
