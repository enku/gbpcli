"""Show differences between two builds"""
import argparse

import yarl

from gbpcli import utils


def handler(args: argparse.Namespace) -> int:
    """Handler for subcommand"""
    url = (
        yarl.URL(args.url) / f"api/builds/{args.machine}/diff/{args.left}/{args.right}"
    )
    response = utils.check(args.session.get(str(url)))

    if len(response["diff"]["items"]) == 0:
        return 0

    print(f"diff -r {args.machine}/{args.left} {args.machine}/{args.right}")
    print(
        f"--- a/{args.machine}/{args.left}"
        f" {utils.timestr(response['diff']['builds'][0]['db']['submitted'])}"
    )
    print(
        f"+++ b/{args.machine}/{args.right}"
        f" {utils.timestr(response['diff']['builds'][1]['db']['submitted'])}"
    )

    last_modified = None
    for change, item in iter(response["diff"]["items"]):
        if change == -1:
            print(f"-{item}")
        elif change == 1:
            print(f"+{item}")
        else:
            if item == last_modified:
                print(f"-{item}")
            else:
                print(f"+{item}")
            last_modified = item

    return 0


def parse_args(parser: argparse.ArgumentParser):
    """Set subcommand arguments"""
    parser.add_argument("machine", help="name of the machine")
    parser.add_argument("left", type=int, help="left build number")
    parser.add_argument("right", type=int, help="right build number")
