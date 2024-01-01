"""Schedule a build for the given machine in CI/CD"""
import argparse

from gbpcli import GBP, Console
from gbpcli.subcommands import completers as comp

HELP = "Schedule a build for the given machine in CI/CD"


def handler(args: argparse.Namespace, gbp: GBP, _console: Console) -> int:
    """Schedule a build for the given machine in CI/CD"""
    params = {}
    for param in args.param or []:
        key, value = param.split("=", 1)
        params[key] = value

    gbp.build(args.machine, **params)

    return 0


def parse_args(parser: argparse.ArgumentParser) -> None:
    """Set subcommand arguments"""
    parser.add_argument(
        "--param", "-p", action="append", help="Build parameter (name=value)"
    )
    comp.set(
        parser.add_argument("machine", metavar="MACHINE", help="name of the machine"),
        comp.machines,
    )
