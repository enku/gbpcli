"""List machines with builds"""
import argparse

import yarl

from gbpcli import utils


def handler(args: argparse.Namespace) -> int:
    """Handler for subcommand"""
    url = yarl.URL(args.url).with_path("/api/machines/")
    response = utils.check(args.session.get(str(url)))

    for machine in response["machines"]:
        print(f"{machine['name']:15} {machine['builds']:>3}")

    return 0


def parse_args(parser: argparse.ArgumentParser):
    """Set subcommand arguments"""
    parser.set_defaults(handler=handler)
