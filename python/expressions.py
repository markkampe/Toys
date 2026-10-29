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
def evaluate(node: ast.Node) -> int:
    """
    recursive descent Evaluate a term in an expression,
        using the pedagogical arithmetic operations

    Parameters:
        node (ast.Node): parsed expression to be evaluated
    Returns:
        (int/float) numerical result
    """
    if isinstance(node, ast.Constant):
        return node.value

    # binary operations
    if isinstance(node, ast.BinOp):
        left = evaluate(node.left)
        right = evaluate(node.right)
        match type(node.op):
            case ast.Add:
                return addition_with_carries(left, right)

            case ast.Sub:
                return subtraction_with_borrows(left, right)

            case ast.Mult:
                return multiply_with_partial_products(left, right)

            case ast.Div:
                quotient, remainder, _steps = long_division(left, right)
                return quotient + remainder/right

            case '_':
                raise TypeError(f"unsupported binary operator: {node.op}")

    # unary operations
    if isinstance(node, ast.UnaryOp):
        match node.op:
            case ast.USub:
                return -node.operand

            case '_':
                raise TypeError(f"unsupported unary operator: {node.op}")

    # those are all the nodes we expect from an eval-parse
    raise TypeError(f"unsupported node type: {node.__class__.__name__}")


def main():
    """
    read expressions and evaluate them using the arithmetic library
    """

    # expressions could be commandline or stdin
    parser = argparse.ArgumentParser(
             description="pedagogical arithemetic calculator")
    parser.add_argument("-v", "--verbose", action='store_true')
    parser.add_argument("-s", "--step_by_step", action='store_true')
    parser.add_argument("expressions", nargs='*', type=str,
                        help="expression to be evaluated")
    args = parser.parse_args()

    # see if we got expressions on the command line
    if len(args.expressions) > 0:
        for _i, expr in enumerate(args.expressions):
            print(f"Expression: {expr}")
            tree = ast.parse(expr, mode='eval')
            result = evaluate(tree.body)
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

        expr = line.strip()
        if not expr:
            sys.exit(0)

        # parse and evaluate the expression
        tree = ast.parse(expr, mode='eval')
        result = evaluate(tree.body)
        if args.verbose:
            print("\n==================")
            print(f"{expr} = {result}\n")
        print()


if __name__ == '__main__':
    main()
