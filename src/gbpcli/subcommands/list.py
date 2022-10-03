"""List builds for the given machines

Key for the "Status" column:

    *: Packages were build for the build
    K: The build has been marked for keeping
    P: This build is published
    N: This build has a note attached

"""
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
    table.add_column("ID", justify="right")
    table.add_column("Built")
    table.add_column("Tags")

    for build in builds:
        assert build.info is not None

        # In the old days, we didn't have a "built" field. Fall back to submitted
        timestamp = (build.info.built or build.info.submitted).astimezone(
            LOCAL_TIMEZONE
        )

        status = (
            f"{'[magenta]*[/magenta]' if build.packages_built else ' '}"
            f"{'[yellow]K[/yellow]' if build.info.keep else ' '}"
            f"{'[bold green]P[/bold green]' if build.info.published else ' '}"
            f"{'[blue]N[/blue]' if build.info.note else ' '}"
        )
        number = f"[bold]{build.number}[/bold]"
        built = f"{timestamp.strftime('%x %X')}"
        tag_list = [f"@{tag}" for tag in build.info.tags] if build.info.tags else []
        tags = f"[yellow]{' '.join(tag_list)}[/yellow]"
        table.add_row(status, number, built, tags)

    console.print(table)

    return 0


def parse_args(parser: argparse.ArgumentParser):
    """Set subcommand arguments"""
    parser.add_argument("machine", metavar="MACHINE", help="name of the machine")
