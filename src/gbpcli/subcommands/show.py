"""Show details for a given build"""
import argparse
import sys
from typing import Optional

from gbpcli import GBP, Build, utils


def handler(args: argparse.Namespace, gbp: GBP) -> int:
    """Handler for "show" subcommand"""
    machine: str = args.machine
    build: Optional[Build]

    if args.number is None:
        build = gbp.latest(machine)

        if build is None:
            print("Not Found", file=sys.stderr)
            return 1
    else:
        build = Build(machine=machine, number=args.number)

    build = gbp.get_build_info(build)

    if build is None:
        print("Build not found", file=sys.stderr)
        return 1

    assert build.info is not None
    print(utils.build_to_str(build), end="")

    return 0


def parse_args(parser):
    """Set subcommand arguments"""
    parser.add_argument("machine", metavar="MACHINE", help="name of the machine")
    parser.add_argument(
        "number", type=int, metavar="NUMBER", help="build number", nargs="?"
    )
