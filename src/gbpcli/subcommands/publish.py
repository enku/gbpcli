"""Publish a build"""
import argparse

import yarl

from gbpcli.utils import check


def handler(args: argparse.Namespace) -> int:
    """Handler for subcommand"""
    url = yarl.URL(args.url) / f"api/builds/{args.machine}/{args.number}/publish"
    check(args.session.post(str(url)))

    return 0


def parse_args(parser: argparse.ArgumentParser):
    """Set subcommand arguments"""
    parser.add_argument("machine", help="name of the machine")
    parser.add_argument("number", type=int, help="build number")
