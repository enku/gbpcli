"""List machines with builds"""
import argparse

from rich import box
from rich.table import Table

from gbpcli import GBP, Console, render, utils


def latest_build_to_str(build: dict) -> str:
    """Return the "Latest" column for the given build"""
    build_id = build["id"].rpartition(".")[2]

    if build["published"]:
        build_id = f"[published]{build_id}[/published]"

    return f"[build_id]{build_id}[/build_id]"


def handler(args: argparse.Namespace, gbp: GBP, console: Console) -> int:
    """List machines with builds"""
    my_machines = utils.get_my_machines_from_args(args)
    machines = [
        machine
        for machine in gbp.machines()
        if not args.mine or machine[0] in my_machines
    ]
    table = Table(
        title=f"{len(machines)} Machines",
        box=box.ROUNDED,
        title_style="header",
        style="box",
    )
    table.add_column("Machine", header_style="header")
    table.add_column("Builds", justify="right", header_style="header")
    table.add_column("Latest", justify="right", header_style="header")

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
