"""Show details for a given build"""
import argparse
import sys
import textwrap

from gbpcli import GBP, Build, NotFound, utils


def handler(args: argparse.Namespace, gbp: GBP) -> int:
    """Handler for subcommand"""
    machine: str = args.machine
    build: Build

    if args.number == 0:
        build = gbp.latest(machine)
    else:
        build = Build(name=machine, number=args.number)

    try:
        build = gbp.get_build_info(build)
    except NotFound:
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
            if len(line) > 70:
                for splitline in textwrap.wrap(note):
                    print(f"    {splitline}")
            else:
                print(f"    {line}")
    return 0


def parse_args(parser):
    """Set subcommand arguments"""
    parser.add_argument("machine", help="name of the machine")
    parser.add_argument("number", type=int, help="build number", nargs="?", default=0)
