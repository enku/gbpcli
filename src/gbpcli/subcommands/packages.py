"""Display the list of packages for a given build"""
import argparse
from typing import cast

from gbpcli import GBP, Console, utils
from gbpcli.subcommands import completers

HELP = """Display the list of packages for a given build"""


def handler(args: argparse.Namespace, gbp: GBP, console: Console) -> int:
    """List a build's packages"""
    build = utils.resolve_build_id(args.machine, args.number, gbp)

    if (packages := gbp.packages(build)) is None:
        console.err.print("Not Found")
        return 1

    for package in packages:
        console.out.print(f"[package]{package}[/package]")

    return 0


# pylint: disable=duplicate-code
def parse_args(parser: argparse.ArgumentParser) -> None:
    """Set subcommand arguments"""
    cast(
        completers.Action,
        parser.add_argument("machine", metavar="MACHINE", help="name of the machine"),
    ).completer = completers.machines
    cast(
        completers.Action,
        parser.add_argument("number", metavar="NUMBER", help="build number"),
    ).completer = completers.build_ids
