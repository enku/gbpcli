"""Keep (or release) a build"""
import argparse

from gbpcli import GBP, Console, utils
from gbpcli.subcommands import completers as comp

HELP = """Keep (or release) a build"""


def handler(args: argparse.Namespace, gbp: GBP, console: Console) -> int:
    """Keep (or release) a build"""
    build = utils.resolve_build_id(args.machine, args.number, gbp)

    if (gbp.release(build) if args.release else gbp.keep(build)) is None:
        console.err.print("Not Found")
        return 1

    return 0


# pylint: disable=duplicate-code
def parse_args(parser: argparse.ArgumentParser) -> None:
    """Set subcommand arguments"""
    parser.add_argument("--release", "-r", action="store_true", default=False)
    comp.set(
        parser.add_argument("machine", metavar="MACHINE", help="name of the machine"),
        comp.machines,
    )
    comp.set(
        parser.add_argument("number", metavar="NUMBER", help="build number"),
        comp.build_ids,
    )
