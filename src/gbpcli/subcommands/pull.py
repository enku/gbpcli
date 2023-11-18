"""Pull a build"""
import argparse

from gbpcli import GBP, Build, Console

HELP = """Pull a build"""


def handler(args: argparse.Namespace, gbp: GBP, _console: Console) -> int:
    """Pull a build"""
    build = Build(machine=args.machine, number=args.number)

    gbp.pull(build, note=args.note)

    return 0


def parse_args(parser: argparse.ArgumentParser) -> None:
    """Set subcommand arguments"""
    parser.add_argument(
        "--note", default=None, metavar="NOTE", help="Build note to attach"
    )
    parser.add_argument("machine", metavar="MACHINE", help="name of the machine")
    parser.add_argument("number", type=int, metavar="NUMBER", help="build number")
