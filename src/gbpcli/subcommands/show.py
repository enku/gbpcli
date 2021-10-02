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
        build = Build(name=machine, number=args.number)

    build = gbp.get_build_info(build)

    if build is None:
        print("Build not found", file=sys.stderr)
        return 1

    assert build.info is not None

    print(f"Build: {build.name}/{build.number}")
    submitted = utils.timestr(build.info.submitted)
    print(f"Submitted: {submitted}")

    assert build.info.completed is not None

    completed = utils.timestr(build.info.completed)
    print(f"Completed: {completed}")

    print(f"Published: {utils.yesno(build.info.published)}")
    print(f"Keep: {utils.yesno(build.info.keep)}")

    if note := build.info.note:
        print("")
        lines = note.split("\n")

        for line in lines:
            print(f"    {line}")

    return 0


def parse_args(parser):
    """Set subcommand arguments"""
    parser.add_argument("machine", metavar="MACHINE", help="name of the machine")
    parser.add_argument(
        "number", type=int, metavar="NUMBER", help="build number", nargs="?"
    )
