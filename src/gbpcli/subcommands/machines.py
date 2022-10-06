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
        build_id = f"[published]{build_id}[/published]"

    return f"[build_id]{build_id}[/build_id]"


def handler(_args: argparse.Namespace, gbp: GBP, console: Console) -> int:
    """Handler for machines subcommand"""
    machines = gbp.machines()
    table = Table(
        title=f"{len(machines)} Machines", box=box.ROUNDED, title_style="header"
    )
    table.add_column("Machine", header_style="header")
    table.add_column("Builds", justify="right", header_style="header")
    table.add_column("Latest", justify="right", header_style="header")

    for machine, builds, latest in machines:
        table.add_row(
            f"[machine]{machine}[/machine]",
            str(builds),
            latest_build_to_str(latest),
        )

    console.print(table)
    return 0


def parse_args(_parser: argparse.ArgumentParser) -> None:
    """Set subcommand arguments"""
