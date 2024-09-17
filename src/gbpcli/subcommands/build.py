"""Schedule a build for the given machine in CI/CD"""

import argparse

from gbpcli import GBP
from gbpcli.subcommands import completers as comp
from gbpcli.types import Console

HELP = "Schedule a build for the given machine in CI/CD"


def handler(args: argparse.Namespace, gbp: GBP, console: Console) -> int:
    """Schedule a build for the given machine in CI/CD"""
    params = {"is_repo": getattr(args, "is_repo", False)}
    for param in args.param or []:
        key, equals, value = param.partition("=")
        if not (key and equals):
            error_msg = "[bold]Build parameters must be of the format name=value[/bold]"
            console.err.print(error_msg)
            return 1
        params[key] = value

    gbp.build(args.machine, **params)

    return 0


def parse_args(parser: argparse.ArgumentParser) -> None:
    """Set subcommand arguments"""
    parser.add_argument(
        "--repo",
        "-r",
        action="store_true",
        default=False,
        dest="is_repo",
        help="The name is a repo instead of a machine",
    )
    parser.add_argument(
        "--param", "-p", action="append", help="Build parameter (name=value)"
    )
    comp.set(
        parser.add_argument(
            "machine", metavar="NAME", help="name of the machine or repo"
        ),
        comp.machines,
    )
