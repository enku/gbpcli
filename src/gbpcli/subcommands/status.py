"""Show details for a given build"""
import argparse
import sys

from rich import box
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from gbpcli import GBP
from gbpcli.utils import resolve_build_id, timestr, yesno


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

    grid.add_row("[bold]Build:[/bold] ", f"[blue]{build.machine}/{build.number}[/blue]")

    grid.add_row("[bold]Submitted:[/bold] ", timestr(build.info.submitted))

    grid.add_row(
        "[bold]Completed:[/bold] ",
        timestr(build.info.completed) if build.info.completed else "no",
    )

    if build.info.built is not None:
        grid.add_row("[bold]BuildDate:[/bold] ", timestr(build.info.built))

    grid.add_row("[bold]Published:[/bold] ", f"{yesno(build.info.published)}")
    grid.add_row("[bold]Keep:[/bold] ", f"{yesno(build.info.keep)}")
    grid.add_row("[bold]Tags:[/bold] ", f"{' '.join(build.info.tags)}")

    packages = build.packages_built
    grid.add_row(
        "[bold]Packages-built:[/bold] ",
        f"[magenta]{packages[0].cpv}[/magenta]" if packages else "None",
    )

    if packages:
        for package in packages[1:]:
            grid.add_row("", f"[magenta]{package.cpv}[/magenta]")

    console.print(Panel(grid, expand=False))

    if note := build.info.note:
        console.print()
        table = Table(box=box.ROUNDED, pad_edge=False)
        table.add_column("📎 Notes")
        table.add_row(note.rstrip("\n"))

        console.print(table)

    return 0


def parse_args(parser: argparse.ArgumentParser) -> None:
    """Set subcommand arguments"""
    parser.add_argument("machine", metavar="MACHINE", help="name of the machine")
    parser.add_argument("number", metavar="NUMBER", help="build number", nargs="?")
