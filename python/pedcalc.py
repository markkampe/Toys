#!/usr/bin/python3
"""
    This is a program to accept simple arithmetic expressions
    and evaluate them with the pedagogical/visual operations
    in the pedarithmetic library.
"""
import sys
import argparse
import pedarithmetic
import factors

# pylint: disable=fixme
# TODO
#   If I need more debugging, I could add a --debug flag to main,
#      and pass it to the Arithmetic constructor, which would then
#      (from the CLI) enable the debug option
arith = pedarithmetic.Arithmetic()
fact = factors.Factors()


# pylint: disable=too-many-branches, too-many-return-statements
def evaluate(tokens: [str]) -> int/float:
    """
    evaluate an arithmetic expressions
    """
    count = len(tokens)
    if count == 1:
        return tokens[0]
    if count > 3:
        sys.stderr.write(f"Invalid expression: {tokens}\n")
        return 0

    # <op><num> | <op><num><num> | <num><op><num>
    left = tokens[0]
    middle = tokens[1]
    if count == 2:      # <op> <num>
        if left in ("factor", "fact", "FACTOR", "FACT"):
            facts = fact.factors(int(middle))
            print(f"factors({middle}): {facts}")
            return 0
        raise TypeError(f"unrecognized operation: {left}")
    right = tokens[2]
    # <op> <num> <num> ?
    if left in ("lcm", "LCM"):
        n = fact.least_common_multiple(int(middle), int(right))
        print(f"LCM({middle}, {right}) = {n}")
        return n
    if left in ("gcf", "GCF"):
        n = fact.greatest_common_factor(int(middle), int(right))
        print(f"GCF({middle}, {right}) = {n}")
        return n

    # <num> <op> <num>
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
            raise TypeError(f"unsupported binary operator: {middle}")


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
