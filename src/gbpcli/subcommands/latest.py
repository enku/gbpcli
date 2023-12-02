"""Show the latest build number for the given machine"""
import argparse

from gbpcli import GBP, Console

HELP = """Show the latest build number for the given machine"""


def handler(args: argparse.Namespace, gbp: GBP, console: Console) -> int:
    """Show the latest build number for a machine"""
    if not (latest_build := gbp.latest(args.machine)):
        console.err.print("No builds exist for the given machine")
        return 1

    console.out.print(latest_build.number)

    return 0


def parse_args(parser: argparse.ArgumentParser) -> None:
    """Set subcommand arguments"""
    parser.add_argument("machine", metavar="MACHINE", help="name of the machine")
