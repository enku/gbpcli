"""Show differences between two builds

If the "left" argument is omitted, it defaults to the build which is published.

If the "right" argument is omitted, it defaults to the most recent build.
"""
import argparse
import sys

from gbpcli import GBP, Change, Status, utils


def handler(args: argparse.Namespace, gbp: GBP) -> int:
    """Handler for subcommand"""
    left = args.left
    right = args.right

    if left is None:
        builds = gbp.builds(args.machine)
        published = [i for i in builds if (i.info and i.info.published)]

        if not published:
            print("No origin specified and no builds published", file=sys.stderr)
            return 1

        assert len(published) == 1
        left = published[0].number

        assert right is None
        right = builds[-1].number

    if right is None:
        latest = gbp.latest(args.machine)

        if latest is None:
            print("Need at least two builds to diff", file=sys.stderr)
            return 1

        right = latest.number

    left_build, right_build, diff = gbp.diff(args.machine, left, right)

    if not diff:
        return 0

    assert left_build.info is not None
    assert right_build.info is not None

    print(f"diff -r {args.machine}/{left} {args.machine}/{right}")
    print(f"--- a/{args.machine}/{left} {utils.timestr(left_build.info.submitted)}")
    print(f"+++ b/{args.machine}/{right} {utils.timestr(right_build.info.submitted)}")

    last_modified: Change | None = None
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


def parse_args(parser: argparse.ArgumentParser) -> None:
    """Set subcommand arguments"""
    parser.add_argument("machine", metavar="MACHINE", help="name of the machine")
    parser.add_argument(
        "left", type=int, metavar="LEFT", nargs="?", help="left build number"
    )
    parser.add_argument(
        "right", type=int, metavar="RIGHT", nargs="?", help="right build number"
    )
