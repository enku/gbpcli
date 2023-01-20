"""Add tag to the given build"""
import argparse
from typing import Optional, TextIO

from rich.console import Console

from gbpcli import GBP, Build, utils


def handler(
    args: argparse.Namespace, gbp: GBP, _console: Console, errorf: TextIO
) -> int:
    """Add tags builds"""
    build: Optional[Build]
    machine: str = args.machine
    tag: str = args.tag

    if args.remove:
        if args.number is not None:
            print("When removing a tag, omit the build number", file=errorf)
            return 1

        if tag.startswith("@"):
            tag = tag[1:]

        gbp.untag(machine, tag)
        return 0

    build = utils.resolve_build_id(machine, args.number, gbp, errorf=errorf)

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
