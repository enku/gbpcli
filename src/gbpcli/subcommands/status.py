"""Show details for a given build"""
import argparse
import sys

from rich import box
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from gbpcli import GBP
from gbpcli.utils import green_yes, resolve_build_id, timestr


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

    if build.info.built is not None:
        grid.add_row("[bold]BuildDate:[/bold] ", timestr(build.info.built))

    grid.add_row("[bold]Submitted:[/bold] ", timestr(build.info.submitted))

    grid.add_row(
        "[bold]Completed:[/bold] ",
        timestr(build.info.completed) if build.info.completed else "no",
    )

    grid.add_row("[bold]Published:[/bold] ", f"{green_yes(build.info.published)}")
    grid.add_row("[bold]Keep:[/bold] ", f"{green_yes(build.info.keep)}")
    tags = [f"[yellow]@{tag}[/yellow]" for tag in build.info.tags]
    grid.add_row("[bold]Tags:[/bold] ", " ".join(tags))

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
