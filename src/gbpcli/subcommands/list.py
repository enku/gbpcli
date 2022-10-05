"""List builds for the given machines

Key for the "Flags" column:

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
        title=f"\N{PERSONAL COMPUTER} [machine]{args.machine}[/machine]",
        box=box.ROUNDED,
        title_style="header",
    )
    table.add_column("Flags", header_style="header")
    table.add_column("ID", justify="right", header_style="header")
    table.add_column("Built", header_style="header")
    table.add_column("Tags", header_style="header")

    for build in builds:
        assert build.info is not None

        # In the old days, we didn't have a "built" field. Fall back to submitted
        timestamp = (build.info.built or build.info.submitted).astimezone(
            LOCAL_TIMEZONE
        )

        flags = (
            f"{'[package]*[/package]' if build.packages_built else ' '}"
            f"{'[keep]K[/keep]' if build.info.keep else ' '}"
            f"{'[published]P[/published]' if build.info.published else ' '}"
            f"{'[note_flag]N[/note_flag]' if build.info.note else ' '}"
        )
        number = f"[build_id]{build.number}[/build_id]"
        built = f"[timestamp]{timestamp.strftime('%x %X')}[/timestamp]"
        tag_list = [f"@{tag}" for tag in build.info.tags] if build.info.tags else []
        tags = f"[tag]{' '.join(tag_list)}[/tag]"
        table.add_row(flags, number, built, tags)

    console.print(table)

    return 0


def parse_args(parser: argparse.ArgumentParser):
    """Set subcommand arguments"""
    parser.add_argument("machine", metavar="MACHINE", help="name of the machine")
