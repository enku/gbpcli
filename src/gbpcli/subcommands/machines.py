"""List machines with builds"""
import argparse

from rich import box
from rich.console import Console
from rich.table import Table

from gbpcli import GBP


def latest_build_to_str(build: dict) -> str:
    """Return the "Latest" column for the given build"""
    build_id = build["id"].rpartition(".")[2]

    if build["published"]:
        build_id = f"[bold green]{build_id}[/bold green]"

    return build_id


def handler(_args: argparse.Namespace, gbp: GBP, console: Console) -> int:
    """Handler for machines subcommand"""
    table = Table(title="Machines", box=box.ROUNDED, title_style="bold")
    table.add_column("Machine")
    table.add_column("Builds", justify="right")
    table.add_column("Latest", justify="right")

    for machine, builds, latest in gbp.machines():
        table.add_row(
            f"[bold blue]{machine}[/bold blue]",
            str(builds),
            latest_build_to_str(latest),
        )

    console.print(table)
    return 0


def parse_args(parser: argparse.ArgumentParser) -> None:
    """Set subcommand arguments"""
    parser.set_defaults(handler=handler)
