"""Display the list of packages for a given build"""
import argparse

from gbpcli import GBP, Console, utils


def handler(args: argparse.Namespace, gbp: GBP, console: Console) -> int:
    """List a build's packages"""
    build = utils.resolve_build_id(args.machine, args.number, gbp)
    packages = gbp.packages(build)

    if packages is None:
        console.err.print("Not Found")
        return 1

    for package in packages:
        console.out.print(f"[package]{package}[/package]")

    return 0


def parse_args(parser: argparse.ArgumentParser) -> None:
    """Set subcommand arguments"""
    parser.add_argument("machine", metavar="MACHINE", help="name of the machine")
    parser.add_argument("number", metavar="NUMBER", help="build number")
