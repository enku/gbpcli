"""Show differences between two builds"""
import argparse

from gbpcli import GBP, Status, utils


def handler(args: argparse.Namespace, gbp: GBP) -> int:
    """Handler for subcommand"""
    left_build, right_build, diff = gbp.diff(args.machine, args.left, args.right)

    if not diff:
        return 0

    print(f"diff -r {args.machine}/{args.left} {args.machine}/{args.right}")
    assert left_build.info is not None
    print(
        f"--- a/{args.machine}/{args.left}"
        f" {utils.timestr(left_build.info.submitted)}"
    )
    assert right_build.info is not None
    print(
        f"+++ b/{args.machine}/{args.right}"
        f" {utils.timestr(right_build.info.submitted)}"
    )

    last_modified = None
    # for change, item in iter(response["diff"]["items"]):
    for item in diff:
        if item.status == Status.REMOVED:
            print(f"-{item.item}")
        elif item.status == Status.ADDED:
            print(f"+{item.item}")
        else:
            if item == last_modified:
                print(f"-{item.item}")
            else:
                print(f"+{item.item}")
            last_modified = item

    return 0


def parse_args(parser: argparse.ArgumentParser):
    """Set subcommand arguments"""
    parser.add_argument("machine", help="name of the machine")
    parser.add_argument("left", type=int, help="left build number")
    parser.add_argument("right", type=int, help="right build number")
