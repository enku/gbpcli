"""List builds for the given machines"""
import argparse

from gbpcli import GBP, LOCAL_TIMEZONE


def handler(args: argparse.Namespace, gbp: GBP) -> int:
    """Handler for subcommand"""
    builds = gbp.builds(args.machine, with_packages=True)

    for build in builds:
        assert build.info is not None
        timestamp = build.info.submitted.astimezone(LOCAL_TIMEZONE)

        print(
            "["
            f"{'*' if build.packages_built else ' '}"
            f"{'K' if build.info.keep else ' '}"
            f"{'P' if build.info.published else ' '}"
            f"{'N' if build.info.note else ' '}"
            "]"
            f" {build.number:>5}"
            f" {timestamp.strftime('%x %X')}"
        )

    return 0


def parse_args(parser: argparse.ArgumentParser):
    """Set subcommand arguments"""
    parser.add_argument("machine", metavar="MACHINE", help="name of the machine")
