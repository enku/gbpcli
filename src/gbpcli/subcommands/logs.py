"""Display logs for the given build"""
import argparse
from typing import TextIO

from rich.console import Console

from gbpcli import GBP, SearchField, render, utils
from gbpcli.subcommands import make_searchable


def search_logs(
    gbp: GBP, args: argparse.Namespace, console: Console, errorf: TextIO
) -> int:
    """--search handler for the notes subcommand"""
    builds = gbp.search(args.machine, SearchField.logs, args.number)

    if not builds:
        print("No matches found", file=errorf)
        return 1

    sep = ""
    for build in builds:  # pylint: disable=duplicate-code
        console.print(sep, end="")
        console.print(
            f"{render.format_machine(build.machine, args)}/"
            f"{render.format_build_number(build.number)}"
        )
        console.print(gbp.logs(build))
        sep = "---\n"

    return 0


def handler(
    args: argparse.Namespace, gbp: GBP, console: Console, errorf: TextIO
) -> int:
    """Show build logs"""
    if args.search:
        return search_logs(gbp, args, console, errorf)

    build = utils.resolve_build_id(args.machine, args.number, gbp, errorf=errorf)
    text = gbp.logs(build)

    if text is None:
        print("Not Found", file=errorf)
        return 1

    console.print(text)

    return 0


def parse_args(parser: argparse.ArgumentParser) -> None:
    """Set subcommand arguments"""
    make_searchable(parser)
