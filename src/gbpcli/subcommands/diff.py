"""Show differences between two builds"""

import argparse
import locale
import re
from collections.abc import Iterable
from dataclasses import dataclass, replace
from functools import cache, partial
from math import ceil
from typing import Any, Self

from gbpcli import GBP, render, utils
from gbpcli.subcommands import completers as comp
from gbpcli.types import Build, BuildInfo, Change, ChangeState, Console

HELP = """Show differences between two builds

If the "left" argument is omitted, it defaults to the build which is published.

If the "right" argument is omitted, it defaults to the most recent build.
"""


@dataclass(frozen=True)
class Package:
    """Changed package info.

    Basically Change turned inside out.
    """

    cp: str
    v: str
    build_id: int
    size: int
    status: ChangeState

    @classmethod
    def from_api(cls, item: Change) -> Self:
        """Return Package from diff query item"""
        assert item.package
        if match := re.match(r"(.*)-(\d.*)", item.package["cpv"]):
            cp, v = match.groups()
            return cls(
                cp, v, item.package["buildId"], item.package["size"], item.status
            )
        raise ValueError(item.package["cpv"])


@dataclass(kw_only=True)
class DiffStats:
    """Diff Stats"""

    upgrade: int = 0
    new: int = 0
    reinstall: int = 0
    remove: int = 0
    download_size: int = 0


def handler(args: argparse.Namespace, gbp: GBP, console: Console) -> int:
    """Handler for subcommand"""
    if (left := get_left_build(args.machine, args.left, gbp)) is None:
        console.err.print("No builds given and no builds published")
        return 1

    if (right := get_right_build(args.machine, args.right, gbp)) is None:
        console.err.print("Need at least two builds to diff")
        return 1

    if left == right:
        return 0

    left_build, right_build, diff = gbp.diff(
        args.machine, left, right, with_packages=args.stat
    )

    if not diff:
        return 0

    left_build = ensure_diffable_build(left_build)
    right_build = ensure_diffable_build(right_build)

    # Make mypy happy :|
    assert left_build.info and left_build.info.built
    assert right_build.info and right_build.info.built

    header = partial(console.out.print, style="header")
    header(f"diff -r {args.machine}/{left} {args.machine}/{right}")
    header(
        f"[removed]--- {args.machine}/{left} {render.timestr(left_build.info.built)}"
    )
    header(
        f"[added]+++ {args.machine}/{right} {render.timestr(right_build.info.built)}"
    )

    print_diff(diff, console, args.stat)

    return 0


def parse_args(parser: argparse.ArgumentParser) -> None:
    """Set subcommand arguments"""
    # pylint: disable=duplicate-code
    comp.set(
        parser.add_argument("machine", metavar="MACHINE", help="name of the machine"),
        comp.machines,
    )
    parser.add_argument(
        "--stat", action="store_true", default=False, help="show package statistics"
    )
    comp.set(
        parser.add_argument(
            "left", metavar="LEFT", nargs="?", help="left build number"
        ),
        comp.build_ids,
    )
    comp.set(
        parser.add_argument(
            "right", metavar="RIGHT", nargs="?", help="right build number"
        ),
        comp.build_ids,
    )


def get_left_build(machine: str, requested: str, gbp: GBP) -> int | None:
    """Return the requested left build number

    - If requested is not None, returns to the requested build (number)
    - If requested is None, return to the published build for the machine
    - If neither of this is possible, return None
    """
    if requested is not None:
        return utils.resolve_build_id(machine, requested, gbp).number

    builds = cached_builds(machine, gbp)
    published = [i for i in builds if (i.info and i.info.published)]

    return published[0].number if published else None


def get_right_build(machine: str, requested: str, gbp: GBP) -> int | None:
    """Return the requested right build number

    - If requested is not None, returns to the requested build (number)
    - If requested is None, return the last built build for the machine
    - If neither of this is possible, return None
    """
    if requested is not None:
        return utils.resolve_build_id(machine, requested, gbp).number

    builds = cached_builds(machine, gbp)

    return builds[-1].number if builds else None


def print_diff(diff: Iterable[Change], console: Console, with_stats: bool) -> None:
    """Given the list of changes, pretty-print the diff to the console"""
    stats = DiffStats()
    previous: Package | None = None
    for item in diff:
        match item.status:
            case ChangeState.REMOVED:
                console.out.print(f"[removed]-{item.item}")
            case ChangeState.ADDED:
                console.out.print(f"[added]+{item.item}")
            case ChangeState.CHANGED:
                console.out.print(f"[removed]-{item.item}")
                console.out.print(f"[added]+{item.item}")

        if with_stats and item.package:
            package = Package.from_api(item)
            aggregate_stats(stats, package, previous)
            previous = package

    if with_stats:
        console.out.print()
        print_stats(stats, console)


def print_stats(stats: DiffStats, console: Console):
    """Print the DiffStats to the Console"""
    added = stats.new + stats.reinstall + stats.upgrade
    line = f"{added} {render.pluralize('package', added)} added"

    if added:
        prefix = ""
        line = f"{line} ("

        for field, suffix in [("upgrade", "s"), ("new", ""), ("reinstall", "s")]:
            if stat := getattr(stats, field):
                line = f"{line}{prefix}{stat} {render.pluralize(field, stat, suffix)}"
                prefix = ", "

        line = f"{line}), Size of downloads: {humansize(stats.download_size)}"

    console.out.print(line)
    console.out.print(
        f"{stats.remove} {render.pluralize('package', stats.remove)} removed"
    )


def aggregate_stats(
    stats: DiffStats, package: Package, previous: Package | None
) -> None:
    """Modify the given DiffStats given the Package"""
    if package.status == ChangeState.ADDED:
        stats.download_size += package.size
        stats.new += 1
        if previous:
            if previous.cp == package.cp:
                stats.upgrade += 1
                stats.new -= 1
                if previous.v == package.v:
                    stats.reinstall += 1
                    stats.upgrade -= 1
    elif package.status == ChangeState.REMOVED:
        stats.remove += 1


def humansize(size: int) -> str:
    """Humanize size (bytes)"""
    locale.setlocale(locale.LC_NUMERIC, "")
    kb = ceil(size / 1024)

    return f"{locale.format_string('%d', kb, grouping=True)} KiB"


@cache
def cached_builds(machine: str, gbp: GBP) -> list[Build]:
    """Return the list of builds for the given machine.

    This is a cached version of GBP.builds()
    """
    return gbp.builds(machine)


def ensure_diffable_build(build: Build) -> Build:
    """Ensure that the build has the right fields to do a diff

    If not replace with dummy values.
    """
    replacements: dict[str, Any] = {}

    if build.info is None or build.info.built is None:
        dummy_info = BuildInfo(
            built=utils.EPOCH,
            keep=False,
            note=None,
            published=False,
            submitted=utils.EPOCH,
            tags=[],
        )
        replacements["info"] = dummy_info
    build = replace(build, **replacements)

    return build
