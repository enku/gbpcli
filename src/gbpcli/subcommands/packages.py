"""Display the list of packages for a given build"""
import argparse
import sys

from gbpcli import GBP, Build


def handler(args: argparse.Namespace, gbp: GBP) -> int:
    """Handler for subcommand"""
    build = Build(machine=args.machine, number=args.number)
    packages = gbp.packages(build)

    if packages is None:
        print("Not Found", file=sys.stderr)
        return 1

    for package in packages:
        print(package)

    return 0


def parse_args(parser: argparse.ArgumentParser):
    """Set subcommand arguments"""
    parser.add_argument("machine", metavar="MACHINE", help="name of the machine")
    parser.add_argument("number", type=int, metavar="NUMBER", help="build number")
