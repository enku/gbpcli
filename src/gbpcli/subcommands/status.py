"""Show details for a given build"""
import argparse
import sys

from rich import box
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from gbpcli import GBP
from gbpcli.utils import resolve_build_id, styled_yes, timestr


def handler(args: argparse.Namespace, gbp: GBP, console: Console) -> int:
    """Handler for "status" subcommand"""
    resolved_build = resolve_build_id(args.machine, args.number, gbp)
    build = gbp.get_build_info(resolved_build)

    if build is None:
        print("Not found", file=sys.stderr)
        return 1

    assert build.info is not None

    grid = Table.grid()
    grid.add_column()
    grid.add_column()

    grid.add_row(
        "[header]Build:[/header] ",
        f"[machine]{build.machine} [build_id]{build.number}[/build_id][/machine]",
    )

    if build.info.built is not None:
        grid.add_row(
            "[header]BuildDate:[/header] ",
            f"[timestamp]{timestr(build.info.built)}[/timestamp]",
        )

    grid.add_row(
        "[header]Submitted:[/header] ",
        f"[timestamp]{timestr(build.info.submitted)}[/timestamp]",
    )

    grid.add_row(
        "[header]Completed:[/header] ",
        f"[timestamp]{timestr(build.info.completed)}[/timestamp]"
        if build.info.completed
        else styled_yes(False),
    )

    grid.add_row("[header]Published:[/header] ", f"{styled_yes(build.info.published)}")
    grid.add_row("[header]Keep:[/header] ", f"{styled_yes(build.info.keep)}")
    tags = [f"[tag]@{tag}[/tag]" for tag in build.info.tags]
    grid.add_row("[header]Tags:[/header] ", " ".join(tags))

    packages = build.packages_built
    grid.add_row(
        "[header]Packages-built:[/header] ",
        f"[package]{packages[0].cpv}[/package]" if packages else "None",
    )

    if packages:
        for package in packages[1:]:
            grid.add_row("", f"[package]{package.cpv}[/package]")

    console.print(Panel(grid, expand=False))

    if note := build.info.note:
        console.print()
        table = Table(box=box.ROUNDED, pad_edge=False)
        table.add_column("📎 Notes", header_style="header")
        table.add_row("[note]" + note.rstrip("\n") + "[/note]")

        console.print(table)

    return 0


def parse_args(parser: argparse.ArgumentParser) -> None:
    """Set subcommand arguments"""
    parser.add_argument("machine", metavar="MACHINE", help="name of the machine")
    parser.add_argument("number", metavar="NUMBER", help="build number", nargs="?")
