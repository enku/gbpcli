"""List builds for the given machines"""
import argparse

from rich import box
from rich.table import Table

from gbpcli import GBP, Console, render
from gbpcli.subcommands import completers as comp

HELP = """List builds for the given machines

Key for the "Flags" column:

    *: Packages were build for the build
    K: The build has been marked for keeping
    P: This build is published
    N: This build has a note attached

"""


def handler(args: argparse.Namespace, gbp: GBP, console: Console) -> int:
    """List a machine's builds"""
    builds = gbp.builds_with_packages(args.machine)
    table = Table(
        title=f"\N{PERSONAL COMPUTER} {render.format_machine(args.machine, args)}",
        box=box.ROUNDED,
        title_style="header",
        style="box",
    )
    table.add_column("Flags", header_style="header")
    table.add_column("ID", justify="right", header_style="header")
    table.add_column("Built", header_style="header")
    table.add_column("Tags", header_style="header")

    for build in builds:
        assert build.info is not None

        # In the old days, we didn't have a "built" field. Fall back to submitted
        timestamp = build.info.built or build.info.submitted

        table.add_row(
            render.format_flags(build),
            render.format_build_number(build.number),
            render.format_timestamp(timestamp.astimezone(render.LOCAL_TIMEZONE)),
            render.format_tags(build.info.tags),
        )

    console.out.print(table)

    return 0


def parse_args(parser: argparse.ArgumentParser) -> None:
    """Set subcommand arguments"""
    comp.set(
        parser.add_argument("machine", metavar="MACHINE", help="name of the machine"),
        comp.machines,
    )
