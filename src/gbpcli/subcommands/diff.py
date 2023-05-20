"""Show differences between two builds

If the "left" argument is omitted, it defaults to the build which is published.

If the "right" argument is omitted, it defaults to the most recent build.
"""
import argparse
import datetime as dt
from collections.abc import Iterable

from rich.console import Console

from gbpcli import GBP, Change, Status, render, utils


def handler(args: argparse.Namespace, gbp: GBP, out: Console, err: Console) -> int:
    """Handler for subcommand"""
    left = args.left
    right = args.right

    if left is None:
        builds = gbp.builds(args.machine)
        published = [i for i in builds if (i.info and i.info.published)]

        if not published:
            err.print("No origin specified and no builds published")
            return 1

        assert len(published) == 1
        left = published[0].number

        assert right is None
        right = str(builds[-1].number)
    else:
        left = utils.resolve_build_id(args.machine, left, gbp).number

    if right is None:
        latest = gbp.latest(args.machine)

        if latest is None:
            err.print("Need at least two builds to diff")
            return 1

        right = latest.number
    else:
        right = utils.resolve_build_id(args.machine, right, gbp).number

    left_build, right_build, diff = gbp.diff(args.machine, left, right)

    if not diff:
        return 0

    assert left_build.info is not None
    assert right_build.info is not None
    assert isinstance(left_build.info.built, dt.datetime)
    assert isinstance(right_build.info.built, dt.datetime)

    out.print(f"diff -r {args.machine}/{left} {args.machine}/{right}", style="header")
    out.print(
        f"--- a/{args.machine}/{left} {render.timestr(left_build.info.built)}",
        style="header",
    )
    out.print(
        f"+++ b/{args.machine}/{right} {render.timestr(right_build.info.built)}",
        style="header",
    )

    print_diff(diff, out)

    return 0


def print_diff(diff: Iterable[Change], out: Console) -> None:
    """Given the list of changes, pretty-print the diff to the console"""
    last_modified: Change | None = None
    # for change, item in iter(response["diff"]["items"]):
    for item in diff:
        if item.status == Status.REMOVED:
            out.print(f"[removed]-{item.item}")
        elif item.status == Status.ADDED:
            out.print(f"[added]+{item.item}")
        else:
            if item == last_modified:
                out.print(f"[removed]-{item.item}")
            else:
                out.print(f"[added]+{item.item}")
            last_modified = item


def parse_args(parser: argparse.ArgumentParser) -> None:
    """Set subcommand arguments"""
    parser.add_argument("machine", metavar="MACHINE", help="name of the machine")
    parser.add_argument("left", metavar="LEFT", nargs="?", help="left build number")
    parser.add_argument("right", metavar="RIGHT", nargs="?", help="right build number")
