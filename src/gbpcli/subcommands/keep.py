"""Keep (or release) a build"""
import argparse
from typing import TextIO

from rich.console import Console

from gbpcli import GBP, utils


def handler(
    args: argparse.Namespace, gbp: GBP, _console: Console, errorf: TextIO
) -> int:
    """Keep (or release) a build"""
    build = utils.resolve_build_id(args.machine, args.number, gbp, errorf=errorf)

    if args.release:
        result = gbp.release(build)
    else:
        result = gbp.keep(build)

    if result is None:
        print("Not Found", file=errorf)
        return 1

    return 0


def parse_args(parser: argparse.ArgumentParser) -> None:
    """Set subcommand arguments"""
    parser.add_argument("--release", "-r", action="store_true", default=False)
    parser.add_argument("machine", metavar="MACHINE", help="name of the machine")
    parser.add_argument("number", metavar="NUMBER", help="build number")
