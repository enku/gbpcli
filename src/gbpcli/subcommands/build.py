"""Schedule a build for the given machine in CI/CD"""
import argparse

from gbpcli import GBP


def handler(args: argparse.Namespace, gbp: GBP) -> int:
    """Handler for subcommand"""
    gbp.build(args.machine)

    return 0


def parse_args(parser: argparse.ArgumentParser) -> None:
    """Set subcommand arguments"""
    parser.add_argument("machine", metavar="MACHINE", help="name of the machine")
