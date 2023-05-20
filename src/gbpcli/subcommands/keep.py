"""Keep (or release) a build"""
import argparse

from gbpcli import GBP, Console, utils


def handler(args: argparse.Namespace, gbp: GBP, console: Console) -> int:
    """Keep (or release) a build"""
    build = utils.resolve_build_id(args.machine, args.number, gbp)

    if args.release:
        result = gbp.release(build)
    else:
        result = gbp.keep(build)

    if result is None:
        console.err.print("Not Found")
        return 1

    return 0


def parse_args(parser: argparse.ArgumentParser) -> None:
    """Set subcommand arguments"""
    parser.add_argument("--release", "-r", action="store_true", default=False)
    parser.add_argument("machine", metavar="MACHINE", help="name of the machine")
    parser.add_argument("number", metavar="NUMBER", help="build number")
