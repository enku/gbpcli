"""Show details for a given build"""
import argparse
import sys

from rich.console import Console

from gbpcli import GBP, utils


def handler(args: argparse.Namespace, gbp: GBP, console: Console) -> int:
    """Handler for "status" subcommand"""
    resolved_build = utils.resolve_build_id(args.machine, args.number, gbp)
    build = gbp.get_build_info(resolved_build)

    if build is None:
        print("Not found", file=sys.stderr)
        return 1

    assert build.info is not None
    console.print(utils.build_to_str(build), end="", highlight=False)

    return 0


def parse_args(parser: argparse.ArgumentParser) -> None:
    """Set subcommand arguments"""
    parser.add_argument("machine", metavar="MACHINE", help="name of the machine")
    parser.add_argument("number", metavar="NUMBER", help="build number", nargs="?")
