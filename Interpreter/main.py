import argparse
import sys
from typing import List

from intepreter import Interpreter


def get_arguments() -> str:
    parser = argparse.ArgumentParser()
    parser.add_argument('filename', help='Path to the source code')
    parser.add_argument('-p', '--printstyle', help='Style of output. "ascii" to print characters and "numbers" to print the value directly', default='ascii', choices=['ascii', 'numbers'])
    args = parser.parse_args()
    return (args.filename, args.printstyle)


def get_code(filename: str) -> List[str]:
    try:
        with open(filename, 'r', encoding='utf-8') as fi:
            return fi.read().lower().splitlines()
    except Exception:
        print(f"Cannot open file '{filename}'.")
        sys.exit()

if __name__ == '__main__':
    filename, print_style = get_arguments()
    interpreter = Interpreter(print_style)
    lines = get_code(filename)
    interpreter.execute(lines)
