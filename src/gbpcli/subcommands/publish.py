"""Publish a build"""
import argparse

from gbpcli import GBP, Console
from gbpcli.utils import resolve_build_id

HELP = """Publish a build

If NUMBER is not specified, defaults to the latest build for the given machine.
"""


def handler(args: argparse.Namespace, gbp: GBP, _console: Console) -> int:
    """Publish a build"""
    build = resolve_build_id(args.machine, args.number, gbp)

    gbp.publish(build)

    return 0


def parse_args(parser: argparse.ArgumentParser) -> None:
    """Set subcommand arguments"""
    parser.add_argument("machine", metavar="MACHINE", help="name of the machine")
    parser.add_argument("number", metavar="NUMBER", nargs="?", help="build number")
