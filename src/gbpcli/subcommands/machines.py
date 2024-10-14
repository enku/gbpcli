"""List machines with builds"""

import argparse
from typing import Any

from rich import box
from rich.table import Table

from gbpcli import GBP, render, utils
from gbpcli.types import Console
from gbpcli.utils import ColumnData, add_columns

HELP = """List machines with builds"""


def handler(args: argparse.Namespace, gbp: GBP, console: Console) -> int:
    """List machines with builds"""
    names = utils.get_my_machines_from_args(args) if args.mine else None
    machines = gbp.machines(names=names)
    table = Table(
        title=f"{len(machines)} Machines",
        box=box.ROUNDED,
        title_style="header",
        style="box",
    )
    rjust = {"justify": "right"}
    columns: ColumnData = [("Machine", {}), ("Builds", rjust), ("Latest", rjust)]
    add_columns(table, columns)

    for machine, builds, latest in machines:
        table.add_row(
            render.format_machine(machine, args),
            str(builds),
            latest_build_to_str(latest),
        )

    console.out.print(table)
    return 0


def parse_args(parser: argparse.ArgumentParser) -> None:
    """Set subcommand arguments"""
    parser.add_argument(
        "--mine",
        action="store_true",
        default=False,
        help="Only display machine info for --my-machines",
    )


def latest_build_to_str(build: dict[str, Any]) -> str:
    """Return the "Latest" column for the given build"""
    build_id = build["id"].rpartition(".")[2]

    if build["published"]:
        build_id = f"[published]{build_id}[/published]"

    return f"[build_id]{build_id}[/build_id]"
