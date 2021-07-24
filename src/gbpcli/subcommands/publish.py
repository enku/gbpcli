"""Publish a build"""
import argparse

from gbpcli import GBP, Build


def handler(args: argparse.Namespace, gbp: GBP) -> int:
    """Handler for subcommand"""
    build: Build
    machine: str = args.machine

    if args.number:
        build = Build(name=machine, number=args.number)
    else:
        build = gbp.latest(machine)

    gbp.publish(build)

    return 0


def parse_args(parser: argparse.ArgumentParser):
    """Set subcommand arguments"""
    parser.add_argument("machine", help="name of the machine")
    parser.add_argument("number", type=int, nargs="?", default=0, help="build number")
