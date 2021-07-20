"""List builds for the given machines"""
import argparse
import datetime
import sys

import yarl

from gbpcli import LOCAL_TIMEZONE


def handler(args: argparse.Namespace) -> int:
    """Handler for subcommand"""
    url = yarl.URL(args.url) / f"api/builds/{args.machine}/"
    response = args.session.get(str(url)).json()

    if error := response["error"]:
        print(error, file=sys.stderr)
        return 1

    for build in response["builds"]:
        timestamp = datetime.datetime.fromisoformat(build["db"]["submitted"])
        timestamp = timestamp.astimezone(LOCAL_TIMEZONE)

        print(
            "["
            f"{'K' if build['db']['keep'] else ' '}"
            f"{'P' if build['storage']['published'] else ' '}"
            f"{'N' if build['db']['note'] else ' '}"
            "]"
            f" {build['number']:>5}"
            f" {timestamp.strftime('%x %X')}"
        )

    return 0


def parse_args(parser: argparse.ArgumentParser):
    """Set subcommand arguments"""
    parser.add_argument("machine", help="name of the machine")
