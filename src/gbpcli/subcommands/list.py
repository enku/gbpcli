"""List builds for the given machines"""

import argparse

from rich import box
from rich.table import Table

from gbpcli import GBP, render
from gbpcli.subcommands import completers as comp
from gbpcli.types import Build, Console
from gbpcli.utils import ColumnData, add_columns

HELP = """List builds for the given machines

Key for the "Flags" column:

    *: Packages were build for the build
    K: The build has been marked for keeping
    P: This build is published
    N: This build has a note attached

"""


def handler(args: argparse.Namespace, gbp: GBP, console: Console) -> int:
    """List a machine's builds"""
    columns: ColumnData
    builds = gbp.builds(args.machine, with_packages=True)
    table = Table(
        title=f"\N{PERSONAL COMPUTER} {render.format_machine(args.machine, args)}",
        box=box.ROUNDED,
        title_style="header",
        style="box",
    )
    columns = [("Flags", {}), ("ID", {"justify": "right"}), ("Built", {}), ("Tags", {})]
    add_columns(table, columns)

    for build in builds:
        add_build_to_row(build, table)

    console.out.print(table)

    return 0


def add_build_to_row(build: Build, table: Table):
    """Add the given Build to the Table"""
    # In the old days, we didn't have a "built" field. Fall back to submitted
    assert build.info is not None

    timestamp = build.info.built or build.info.submitted

    table.add_row(
        render.format_flags(build),
        render.format_build_number(build.number),
        render.format_timestamp(timestamp.astimezone(render.LOCAL_TIMEZONE)),
        render.format_tags(build.info.tags),
    )


def parse_args(parser: argparse.ArgumentParser) -> None:
    """Set subcommand arguments"""
    comp.set(
        parser.add_argument("machine", metavar="MACHINE", help="name of the machine"),
        comp.machines,
    )
