"""List machines with builds"""
import argparse

from rich import box
from rich.console import Console
from rich.table import Table

from gbpcli import GBP


def handler(_args: argparse.Namespace, gbp: GBP, console: Console) -> int:
    """Handler for machines subcommand"""
    table = Table(title="Machines", box=box.ROUNDED, title_style="bold")
    table.add_column("Name")
    table.add_column("Builds", justify="right")

    for machine, builds in gbp.machines():
        table.add_row(f"[bold]{machine}[/bold]", str(builds))

    console.print(table)
    return 0


def parse_args(parser: argparse.ArgumentParser) -> None:
    """Set subcommand arguments"""
    parser.set_defaults(handler=handler)
