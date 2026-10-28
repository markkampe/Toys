#!/usr/bin/python3
"""
    This is a program to accept simple arithmetic expressions
    and evaluate them with the pedagogical/visual operations
    in the arithmetic library.
"""
import sys
import argparse
import ast
from arithmetic import (
    addition_with_carries, subtraction_with_borrows,
    multiply_with_partial_products, long_division
)


# pylint: disable=too-many-branches
def evaluate(node):
    """
    Evaluate a term in an expression using arithmetic functions
    @param node (ast.Node): expression to be evaluated
    @return (int/float) numerical result
    """
    if isinstance(node, ast.Constant):
        return node.value

    if isinstance(node, ast.BinOp):
        left = evaluate(node.left)
        right = evaluate(node.right)
        match type(node.op):
            case ast.Add:
                correct = left + right
                computed = addition_with_carries(left, right)
                if correct != computed:
                    sys.stderr.write(f"ERROR: {left}+{right}->{computed}\n")

            case ast.Sub:
                correct = left - right
                computed = subtraction_with_borrows(left, right)
                if correct != computed:
                    sys.stderr.write(f"ERROR: {left}-{right}->{computed}\n")

            case ast.Mult:
                correct = left * right
                computed = multiply_with_partial_products(left, right)
                if correct != computed:
                    sys.stderr.write(f"ERROR: {left}*{right}->{computed}\n")

            case ast.Div:
                correct = left / right
                quotient, remainder, _steps = long_division(left, right)
                computed = quotient + remainder/right
                if correct != computed:
                    sys.stderr.write(f"ERROR: {left}/{right}->{computed}\n")

            case '_':
                raise TypeError(f"unsupported binary operator: {node.op}")

        return correct

    if isinstance(node, ast.UnaryOp):
        match node.op:
            case ast.USub:
                correct = - node.operand
                return correct

            case ast.UAdd:
                correct = node.operand
                return correct

    raise TypeError(f"unsupported node type: {node.__class__.__name__}")


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
            tree = ast.parse(expr, mode='eval')
            result = evaluate(tree.body)
            print("\n==================")
            print(f"{expr} = {result}")
        sys.exit(0)

    # process expressions from stdin
    while True:
        try:
            line = input("expression: ")
        except EOFError:
            print("\n")
            sys.exit(0)

        expr = line.strip()
        if not expr:
            sys.exit(0)

        # parse and evaluate the expression
        tree = ast.parse(expr, mode='eval')
        result = evaluate(tree.body)
        print("\n==================")
        print(f"{expr} = {result}")


if __name__ == '__main__':
    main()
