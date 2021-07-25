"""Display logs for the given build"""
import argparse
import sys

from gbpcli import GBP, Build, NotFound


def handler(args: argparse.Namespace, gbp: GBP) -> int:
    """Handler for subcommand"""
    build = Build(name=args.machine, number=args.number)

    try:
        text = gbp.logs(build)
    except NotFound:
        print("Not Found", file=sys.stderr)
        return 1

    print(text)

    return 0


def parse_args(parser: argparse.ArgumentParser):
    """Set subcommand arguments"""
    parser.add_argument("machine", metavar="MACHINE", help="name of the machine")
    parser.add_argument("number", type=int, metavar="NUMBER", help="build number")
    parser.set_defaults(handler=handler)
