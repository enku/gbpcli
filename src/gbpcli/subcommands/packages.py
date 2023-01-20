"""Display the list of packages for a given build"""
import argparse
from typing import TextIO

from rich.console import Console

from gbpcli import GBP, utils


def handler(
    args: argparse.Namespace, gbp: GBP, console: Console, errorf: TextIO
) -> int:
    """List a build's packages"""
    build = utils.resolve_build_id(args.machine, args.number, gbp, errorf=errorf)
    packages = gbp.packages(build)

    if packages is None:
        print("Not Found", file=errorf)
        return 1

    for package in packages:
        console.print(f"[package]{package}[/package]")

    return 0


def parse_args(parser: argparse.ArgumentParser) -> None:
    """Set subcommand arguments"""
    parser.add_argument("machine", metavar="MACHINE", help="name of the machine")
    parser.add_argument("number", metavar="NUMBER", help="build number")
