"""Show details for a given build"""
import argparse

from rich import box
from rich.panel import Panel
from rich.table import Table

from gbpcli import GBP, Console
from gbpcli.render import styled_yes, timestr, yesno
from gbpcli.utils import resolve_build_id


def handler(args: argparse.Namespace, gbp: GBP, console: Console) -> int:
    """Show build details"""
    resolved_build = resolve_build_id(args.machine, args.number, gbp)
    build = gbp.get_build_info(resolved_build)

    if build is None:
        console.err.print("Not found")
        return 1

    assert build.info is not None

    grid = Table.grid()
    grid.add_column()
    grid.add_column()

    grid.add_row(
        "[header]Build:[/header] ",
        f"[machine]{build.machine} [build_id]{build.number}[/build_id][/machine]",
    )

    if build.info.built is not None:
        grid.add_row(
            "[header]BuildDate:[/header] ",
            f"[timestamp]{timestr(build.info.built)}[/timestamp]",
        )

    grid.add_row(
        "[header]Submitted:[/header] ",
        f"[timestamp]{timestr(build.info.submitted)}[/timestamp]",
    )

    grid.add_row(
        "[header]Completed:[/header] ",
        f"[timestamp]{timestr(build.info.completed)}[/timestamp]"
        if build.info.completed
        else styled_yes(yesno(False)),
    )

    grid.add_row(
        "[header]Published:[/header] ", f"{styled_yes(yesno(build.info.published))}"
    )
    grid.add_row("[header]Keep:[/header] ", f"{styled_yes(yesno(build.info.keep))}")
    tags = [f"[tag]@{tag}[/tag]" for tag in build.info.tags]
    grid.add_row("[header]Tags:[/header] ", " ".join(tags))

    packages = build.packages_built
    grid.add_row(
        "[header]Packages-built:[/header] ",
        f"[package]{packages[0].cpv}[/package]" if packages else "None",
    )

    if packages:
        for package in packages[1:]:
            grid.add_row("", f"[package]{package.cpv}[/package]")

    console.out.print(Panel(grid, expand=False, style="box"))

    if note := build.info.note:
        console.out.print()
        table = Table(box=box.ROUNDED, pad_edge=False, style="box")
        table.add_column("📎 Notes", header_style="header")
        table.add_row("[note]" + note.rstrip("\n") + "[/note]")

        console.out.print(table)

    return 0


def parse_args(parser: argparse.ArgumentParser) -> None:
    """Set subcommand arguments"""
    parser.add_argument("machine", metavar="MACHINE", help="name of the machine")
    parser.add_argument("number", metavar="NUMBER", help="build number", nargs="?")
