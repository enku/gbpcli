"""Keep (or release) a build"""
import argparse
import sys

from gbpcli import GBP, Build


def handler(args: argparse.Namespace, gbp: GBP) -> int:
    """Handler for "keep" subcommand"""
    build = Build(name=args.machine, number=args.number)

    if args.release:
        result = gbp.release(build)
    else:
        result = gbp.keep(build)

    if result is None:
        print("Not Found", file=sys.stderr)
        return 1

    return 0


def parse_args(parser):
    """Set subcommand arguments"""
    parser.add_argument("--release", "-r", action="store_true", default=False)
    parser.add_argument("machine", metavar="MACHINE", help="name of the machine")
    parser.add_argument("number", type=int, metavar="NUMBER", help="build number")
