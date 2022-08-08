"""Add tag to the given build"""
import argparse
import sys
from typing import Optional

from rich.console import Console

from gbpcli import GBP, Build


def handler(args: argparse.Namespace, gbp: GBP, _console: Console) -> int:
    """Handler for subcommand"""
    build: Optional[Build]
    machine: str = args.machine
    tag: str = args.tag

    if args.remove:
        if args.number is not None:
            print("When removing a tag, omit the build number", file=sys.stderr)
            return 1

        gbp.untag(machine, tag)
        return 0

    if args.number is None:
        build = gbp.latest(machine)
    else:
        build = Build(machine=machine, number=args.number)

    if build is None:
        print("Not Found", file=sys.stderr)
        return 1

    gbp.tag(build, tag)

    return 0


def parse_args(parser: argparse.ArgumentParser) -> None:
    """Set subcommand arguments"""
    parser.add_argument(
        "--remove",
        "-r",
        action="store_true",
        default=False,
        help="Remove the given tag for the machine",
    )
    parser.add_argument("machine", metavar="MACHINE", help="name of the machine")
    parser.add_argument(
        "number", type=int, metavar="NUMBER", nargs="?", help="build number"
    )
    parser.add_argument("tag", type=str, metavar="TAG", help="build tag")
