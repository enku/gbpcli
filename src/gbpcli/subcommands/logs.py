"""Display logs for the given build"""
import argparse
import sys

import yarl


def handler(args: argparse.Namespace) -> int:
    """Handler for subcommand"""
    url = yarl.URL(args.url) / f"api/builds/{args.machine}/{args.number}/log"
    response = args.session.get(str(url))

    if response.status_code == 404:
        print("Not Found", file=sys.stderr)

        return 1

    print(response.text)

    return 0


def parse_args(parser: argparse.ArgumentParser):
    """Set subcommand arguments"""
    parser.add_argument("machine", help="name of the machine")
    parser.add_argument("number", type=int, help="build number")
    parser.set_defaults(handler=handler)
