#!/usr/bin/python3
"""
    This is a program to accept simple arithmetic expressions
    and evaluate them with the pedagogical/visual operations
    in the pedarithmetic library.
"""
import sys
import argparse
import pedarithmetic

arith = pedarithmetic.Arithmetic()


# pylint: disable=too-many-branches, too-many-return-statements
def evaluate(tokens: [str]) -> int/float:
    """
    evaluate an arithmetic expressions
    """
    count = len(tokens)
    if count == 1:
        return tokens[0]
    if count != 3:
        sys.stderr.write(f"Invalid expression: {tokens}\n")
        return 0

    # <num><op><num> or <op> <num> <num>
    left = tokens[0]
    middle = tokens[1]
    right = tokens[2]
    if left in ("lcm", "LCM"):
        return arith.least_common_multiple(middle, right)
    if left in ("gcf", "GCF"):
        return arith.greatest_common_factor(middle, right)

    match middle:
        case '+':
            return arith.addition_with_carries(left, right)
        case '-':
            return arith.subtraction_with_borrows(left, right)
        case '*':
            return arith.multiply_with_partial_products(left, right)
        case '/':
            quotient, remainder = arith.long_division(left, right)
            return quotient + remainder/float(right)
        case '^':
            return arith.exponentiation(left, right)
        case '_':
            raise TypeError(f"unsupported unary operator: {tokens[1]}")


def lex(string: str) -> [str]:
    """
    simple lexer for arithmetic expressions
        recognizes numbers, operators and other alphanumeric strings
        blanks not required between operators and other strings
    """
    start = 0
    in_token = False
    tokens = []
    for index, char in enumerate(string):
        if char in " \t":
            if in_token:
                tokens.append(string[start:index])
                in_token = False
        elif char in "+-*/^":
            if in_token:
                tokens.append(string[start:index])
                in_token = False
            tokens.append(char)
        else:   # likely a number or alphabetic
            if not in_token:
                start = index
                in_token = True

    # string probably ends immediately after last token
    if in_token:
        tokens.append(string[start:])
    return tokens


def main():
    """
    read expressions and evaluate them using the arithmetic library
    """
    # expressions could be commandline or stdin
    parser = argparse.ArgumentParser(
             description="pedagogical arithemetic calculator")
    parser.add_argument("-v", "--verbose", action='store_true')
    parser.add_argument("expressions", nargs='*', type=str,
                        help="expression to be evaluated")
    args = parser.parse_args()

    # see if we got expressions on the command line
    if len(args.expressions) > 0:
        for _i, expr in enumerate(args.expressions):
            print(f"Expression: {expr}")
            tokens = lex(expr)
            result = evaluate(tokens)
            if args.verbose:
                print("\n==================")
                print(f"{expr} = {result}\n")
            print()
        sys.exit(0)

    # process expressions from stdin
    while True:
        try:
            line = input("expression: ")
        except EOFError:
            print("\n")
            sys.exit(0)

        # parse and evaluate the expression
        tokens = lex(line)
        if len(tokens) > 0:
            result = evaluate(tokens)
            if args.verbose:
                print("\n==================")
                print(f"{line} = {result}\n")
        print()


if __name__ == '__main__':
    main()
