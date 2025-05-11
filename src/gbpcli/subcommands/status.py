"""Show details for a given build"""

import argparse
import datetime as dt

from rich import box
from rich.panel import Panel
from rich.table import Table

from gbpcli import GBP
from gbpcli.render import styled_yes, timestr, yesno
from gbpcli.subcommands import completers as comp
from gbpcli.types import Build, Console, Package
from gbpcli.utils import resolve_build_id

HELP = """Show details for a given build"""


def handler(args: argparse.Namespace, gbp: GBP, console: Console) -> int:
    """Show build details"""
    resolved_build = resolve_build_id(args.machine, args.number, gbp)

    if (build := gbp.get_build_info(resolved_build)) is None:
        console.err.print("Not found")
        return 1

    assert build.info is not None

    grid = create_grid()
    col2 = f"[machine]{build.machine} [build_id]{build.number}[/build_id][/machine]"
    add_row(grid, "Build", col2)
    add_timestamps_to_grid(grid, build)
    add_row(grid, "Published", f"{styled_yes(yesno(build.info.published))}")
    add_row(grid, "Keep", f"{styled_yes(yesno(build.info.keep))}")
    tags = [f"[tag]@{tag}[/tag]" for tag in build.info.tags]
    add_row(grid, "Tags", " ".join(tags))
    add_packages(build.packages_built, grid)
    console.out.print(Panel(grid, expand=False, style="box"))
    print_note(console, build.info.note)

    return 0


def create_grid() -> Table:
    """Create and return a grid with the specified number of columns"""
    return Table.grid("", "")


def add_timestamps_to_grid(grid: Table, build: Build) -> None:
    """Add build timestamps to the grid as rows.

    Timestamps include:

        - build time
        - submitted time
        - completed time
    """
    assert build.info is not None
    if build.info.built is not None:
        timestamp_row("BuildDate", build.info.built, grid)
    timestamp_row("Submitted", build.info.submitted, grid)
    timestamp_row("Completed", build.info.completed, grid)


def print_note(console: Console, note: str | None) -> None:
    """Print the given note to console.out

    If not is None, do nothing.
    """
    if not note:
        return

    console.out.print()
    table = Table(
        "📎 Notes", box=box.ROUNDED, pad_edge=False, style="box", header_style="header"
    )
    note = note.rstrip("\n")
    table.add_row(f"[note]{note}[/note]")

    console.out.print(table)


# pylint: disable=duplicate-code
def parse_args(parser: argparse.ArgumentParser) -> None:
    """Set subcommand arguments"""
    comp.set(
        parser.add_argument("machine", metavar="MACHINE", help="name of the machine"),
        comp.machines,
    )
    comp.set(
        parser.add_argument("number", metavar="NUMBER", help="build number", nargs="?"),
        comp.build_ids,
    )


def timestamp_row(header: str, timestamp: dt.datetime | None, grid: Table) -> None:
    """Add a header with a timestamp"""
    if timestamp:
        col2 = f"[timestamp]{timestr(timestamp)}[/timestamp]"
    else:
        col2 = styled_yes(yesno(False))
    add_row(grid, header, col2)


def add_packages(packages: list[Package] | None, grid: Table) -> None:
    """Add the packages header and list"""
    packages = packages or []
    add_row(
        grid,
        "Packages-built",
        f"[package]{packages[0].cpv}[/package]" if packages else "None",
    )
    for package in packages[1:]:
        add_row(grid, "", f"[package]{package.cpv}[/package]")


def add_row(grid: Table, col1: str, col2: str) -> None:
    """Add  2-column row to the given grid"""
    sep = ":" if col1 else ""
    grid.add_row(f"[header]{col1}{sep} [/header]", col2)
