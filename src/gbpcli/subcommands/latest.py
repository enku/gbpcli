"""Show the latest build number for the given machine"""
import argparse
import sys

from gbpcli import GBP


def handler(args: argparse.Namespace, gbp: GBP) -> int:
    """Handler for subcommand"""
    latest_build = gbp.latest(args.machine)
    if not latest_build:
        print("No builds exist for the given machine", file=sys.stderr)
        return 1

    print(latest_build.number)

    return 0


def parse_args(parser: argparse.ArgumentParser):
    """Set subcommand arguments"""
    parser.add_argument("machine", metavar="MACHINE", help="name of the machine")
