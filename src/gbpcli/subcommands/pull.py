"""Pull a build"""
import argparse

from rich.console import Console

from gbpcli import GBP, Build


def handler(args: argparse.Namespace, gbp: GBP, _console: Console) -> int:
    """Handler for the pull subcommand"""
    build = Build(machine=args.machine, number=args.number)

    gbp.pull(build)

    return 0


def parse_args(parser: argparse.ArgumentParser) -> None:
    """Set subcommand arguments"""
    parser.add_argument("machine", metavar="MACHINE", help="name of the machine")
    parser.add_argument("number", type=int, metavar="NUMBER", help="build number")
