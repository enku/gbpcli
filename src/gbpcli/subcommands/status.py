"""Show details for a given build"""
import argparse
import datetime as dt

from rich import box
from rich.panel import Panel
from rich.table import Table

from gbpcli import GBP, Console, Package
from gbpcli.render import styled_yes, timestr, yesno
from gbpcli.subcommands import completers as comp
from gbpcli.utils import resolve_build_id

HELP = """Show details for a given build"""


def handler(args: argparse.Namespace, gbp: GBP, console: Console) -> int:
    """Show build details"""
    resolved_build = resolve_build_id(args.machine, args.number, gbp)

    if (build := gbp.get_build_info(resolved_build)) is None:
        console.err.print("Not found")
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
        timestamp_row("BuildDate", build.info.built, grid)
    timestamp_row("Submitted", build.info.submitted, grid)
    timestamp_row("Completed", build.info.completed, grid)

    grid.add_row(
        "[header]Published:[/header] ", f"{styled_yes(yesno(build.info.published))}"
    )
    grid.add_row("[header]Keep:[/header] ", f"{styled_yes(yesno(build.info.keep))}")
    tags = [f"[tag]@{tag}[/tag]" for tag in build.info.tags]
    grid.add_row("[header]Tags:[/header] ", " ".join(tags))
    add_packages(build.packages_built, grid)

    console.out.print(Panel(grid, expand=False, style="box"))

    if note := build.info.note:
        console.out.print()
        table = Table(box=box.ROUNDED, pad_edge=False, style="box")
        table.add_column("📎 Notes", header_style="header")
        table.add_row("[note]" + note.rstrip("\n") + "[/note]")

        console.out.print(table)

    return 0


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


def timestamp_row(header: str, timestamp: dt.datetime | None, table: Table) -> None:
    """Add a header with a timestamp"""
    table.add_row(
        f"[header]{header}:[/header] ",
        f"[timestamp]{timestr(timestamp)}[/timestamp]"
        if timestamp
        else styled_yes(yesno(False)),
    )


def add_packages(packages: list[Package] | None, table: Table) -> None:
    """Add the packages header and list"""
    packages = packages or []
    table.add_row(
        "[header]Packages-built:[/header] ",
        f"[package]{packages[0].cpv}[/package]" if packages else "None",
    )
    for package in packages[1:]:
        table.add_row("", f"[package]{package.cpv}[/package]")
