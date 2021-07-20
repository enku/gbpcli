"""Command Line interface for Gentoo Build Publisher"""
import argparse
import datetime
import os
import sys
from importlib.metadata import entry_points

import requests

LOCAL_TIMEZONE = datetime.datetime.now().astimezone().tzinfo
DEFAULT_URL = os.getenv("BUILD_PUBLISHER_URL", "https://gbp/")


class NotFound(Exception):
    """Raised when a build does not exist"""


class APIError(Exception):
    """When an error is returned by the REST API"""

    def __init__(self, msg, json):
        super().__init__(msg)
        self.json = json


class UnexpectedResponseError(Exception):
    """Got an unexpected response from the server"""

    def __init__(self, response: requests.Response):
        super().__init__("Unexpected server response")
        self.response = response


def build_parser() -> argparse.ArgumentParser:
    """Set command-line arguments"""
    parser = argparse.ArgumentParser(prog="gbp")
    parser.add_argument("--url", type=str, help="GBP url", default=DEFAULT_URL)
    subparsers = parser.add_subparsers()

    for entry_point in entry_points()["gbpcli.subcommands"]:
        module = entry_point.load()
        subparser = subparsers.add_parser(entry_point.name, help=module.__doc__)
        module.parse_args(subparser)
        subparser.set_defaults(func=module.handler)

    return parser


def main(argv=None) -> int:
    """Main entry point"""
    if argv is None:
        argv = sys.argv[1:]

    parser = build_parser()
    session = requests.Session()
    parser.set_defaults(session=session)

    args = parser.parse_args(argv)

    if not hasattr(args, "func"):
        parser.print_help(file=sys.stderr)
        return 1

    try:
        return args.func(args)
    except (APIError, UnexpectedResponseError) as error:
        print(str(error), file=sys.stderr)

        return 1
