"""List builds for the given machines"""
import argparse

from rich import box
from rich.console import Console
from rich.table import Table

from gbpcli import GBP, LOCAL_TIMEZONE


def handler(args: argparse.Namespace, gbp: GBP, console: Console) -> int:
    """Handler for subcommand"""
    builds = gbp.builds(args.machine, with_packages=True)
    table = Table(
        title=f"\N{PERSONAL COMPUTER} {args.machine}",
        box=box.ROUNDED,
        title_style="bold",
    )
    table.add_column("Status")
    table.add_column("ID")
    table.add_column("Submitted")
    table.add_column("Tags")

    for build in builds:
        assert build.info is not None
        timestamp = build.info.submitted.astimezone(LOCAL_TIMEZONE)
        status = (
            f"{'[magenta]*[/magenta]' if build.packages_built else ' '}"
            f"{'[yellow]K[/yellow]' if build.info.keep else ' '}"
            f"{'[bold green]P[/bold green]' if build.info.published else ' '}"
            f"{'[blue]N[/blue]' if build.info.note else ' '}"
        )
        number = f" [bold]{build.number:>5}[/bold]"
        submitted = f"{timestamp.strftime('%x %X')}"
        tag_list = [f"@{tag}" for tag in build.info.tags] if build.info.tags else []
        tags = f"[yellow]{' '.join(tag_list)}[/yellow]"
        table.add_row(status, number, submitted, tags)

    console.print(table)

    return 0


def parse_args(parser: argparse.ArgumentParser):
    """Set subcommand arguments"""
    parser.add_argument("machine", metavar="MACHINE", help="name of the machine")
