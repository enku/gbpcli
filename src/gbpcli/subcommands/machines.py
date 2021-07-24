"""List machines with builds"""
import argparse

from gbpcli import GBP


def handler(_args: argparse.Namespace, gbp: GBP) -> int:
    """Handler for machines subcommand"""
    for machine, builds in gbp.machines():
        print(f"{machine:15} {builds:>3}")

    return 0


def parse_args(parser: argparse.ArgumentParser):
    """Set subcommand arguments"""
    parser.set_defaults(handler=handler)
