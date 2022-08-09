"""Display logs for the given build"""
import argparse
import sys

from rich.console import Console

from gbpcli import GBP, utils


def handler(args: argparse.Namespace, gbp: GBP, console: Console) -> int:
    """Handler for subcommand"""
    build = utils.resolve_build_id(args.machine, args.number, gbp)
    text = gbp.logs(build)

    if text is None:
        print("Not Found", file=sys.stderr)
        return 1

    console.print(text)

    return 0


def parse_args(parser: argparse.ArgumentParser) -> None:
    """Set subcommand arguments"""
    parser.add_argument("machine", metavar="MACHINE", help="name of the machine")
    parser.add_argument("number", metavar="NUMBER", help="build number")
    parser.set_defaults(handler=handler)
