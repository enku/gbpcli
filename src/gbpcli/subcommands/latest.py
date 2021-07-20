"""Show the latest build number for the given machine"""
import argparse
import sys

import yarl


def handler(args: argparse.Namespace) -> int:
    """Handler for subcommand"""
    url = yarl.URL(args.url).with_path(f"/api/builds/{args.machine}/latest")
    response = args.session.get(str(url)).json()

    if error := response["error"]:
        print(error, file=sys.stderr)
        return 1

    print(response["number"])

    return 0


def parse_args(parser: argparse.ArgumentParser):
    """Set subcommand arguments"""
    parser.add_argument("machine", help="name of the machine")
