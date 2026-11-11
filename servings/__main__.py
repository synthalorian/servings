"""Command line: servings scale --from N --to M."""

import argparse
import sys
from decimal import Decimal, InvalidOperation

from servings.scale import LineError, scale_line


def decimal_value(text):
    try:
        return Decimal(text)
    except InvalidOperation as exc:
        raise argparse.ArgumentTypeError("must be a number") from exc


def positive_decimal(text):
    number = decimal_value(text)
    if number <= 0:
        raise argparse.ArgumentTypeError("must be > 0")
    return number


def build_parser():
    parser = argparse.ArgumentParser(prog="servings")
    sub = parser.add_subparsers(dest="command", required=True)
    scale = sub.add_parser("scale")
    scale.add_argument("--from", dest="from_servings", required=True, type=positive_decimal)
    scale.add_argument("--to", dest="to_servings", required=True, type=decimal_value)
    return parser


def main(argv=None):
    args = build_parser().parse_args(argv)
    for number, line in enumerate(sys.stdin, start=1):
        try:
            print(scale_line(line, args.from_servings, args.to_servings))
        except LineError as exc:
            print(f"line {number}: {exc}", file=sys.stderr)
            return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
