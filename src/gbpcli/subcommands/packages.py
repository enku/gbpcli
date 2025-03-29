"""Display the list of packages for a given build"""

import argparse

from gbpcli import GBP, utils
from gbpcli.subcommands import completers as comp
from gbpcli.types import Console

HELP = """Display the list of packages for a given build"""


def handler(args: argparse.Namespace, gbp: GBP, console: Console) -> int:
    """List a build's packages"""
    build = utils.resolve_build_id(args.machine, args.number, gbp)

    if (packages := gbp.packages(build, args.build_ids)) is None:
        console.err.print("Not Found")
        return 1

    for package in packages:
        console.out.print(f"[package]{package}[/package]")

    return 0


def parse_args(parser: argparse.ArgumentParser) -> None:
    """Set subcommand arguments"""
    parser.add_argument(
        "-b",
        "--build-ids",
        action="store_true",
        default=False,
        help="Include the packages' build ids in the response",
    )
    comp.set(
        parser.add_argument("machine", metavar="MACHINE", help="name of the machine"),
        comp.machines,
    )
    comp.set(
        parser.add_argument("number", metavar="NUMBER", help="build number"),
        comp.build_ids,
    )
