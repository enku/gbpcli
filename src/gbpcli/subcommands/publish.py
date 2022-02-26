"""Publish a build

If NUMBER is not specified, defaults to the latest build for the given machine.
"""
import argparse
import sys
from typing import Optional

from gbpcli import GBP, Build


def handler(args: argparse.Namespace, gbp: GBP) -> int:
    """Handler for subcommand"""
    build: Optional[Build]
    machine: str = args.machine

    if args.number is None:
        build = gbp.latest(machine)
    else:
        build = Build(machine=machine, number=args.number)

    if build is None:
        print("Not Found", file=sys.stderr)
        return 1

    gbp.publish(build)

    return 0


def parse_args(parser: argparse.ArgumentParser):
    """Set subcommand arguments"""
    parser.add_argument("machine", metavar="MACHINE", help="name of the machine")
    parser.add_argument(
        "number", type=int, metavar="NUMBER", nargs="?", help="build number"
    )
