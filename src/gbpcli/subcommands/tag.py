"""Add tag to the given build"""
import argparse
import sys
from typing import Optional

from rich.console import Console

from gbpcli import GBP, Build, utils


def handler(args: argparse.Namespace, gbp: GBP, _console: Console) -> int:
    """Handler for subcommand"""
    build: Optional[Build]
    machine: str = args.machine
    tag: str = args.tag

    if args.remove:
        if args.number is not None:
            print("When removing a tag, omit the build number", file=sys.stderr)
            return 1

        if tag.startswith("@"):
            tag = tag[1:]

        gbp.untag(machine, tag)
        return 0

    build = utils.resolve_build_id(machine, args.number, gbp)

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
    parser.add_argument("number", metavar="NUMBER", nargs="?", help="build number")
    parser.add_argument("tag", type=str, metavar="TAG", help="build tag")
