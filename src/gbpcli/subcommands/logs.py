"""Display logs for the given build"""
import argparse

from gbpcli import GBP, Console, SearchField, render, utils
from gbpcli.subcommands import make_searchable

HELP = """Display logs for the given build"""


def handler(args: argparse.Namespace, gbp: GBP, console: Console) -> int:
    """Show build logs"""
    if args.search:
        return search_logs(gbp, args, console)

    build = utils.resolve_build_id(args.machine, args.number, gbp)

    if (text := gbp.logs(build)) is None:
        console.err.print("Not Found")
        return 1

    console.out.print(text)

    return 0


def parse_args(parser: argparse.ArgumentParser) -> None:
    """Set subcommand arguments"""
    make_searchable(parser)


def search_logs(gbp: GBP, args: argparse.Namespace, console: Console) -> int:
    """--search handler for the notes subcommand"""
    if not (builds := gbp.search(args.machine, SearchField.logs, args.number)):
        console.err.print("No matches found")
        return 1

    sep = ""
    for build in builds:  # pylint: disable=duplicate-code
        console.out.print(sep, end="")
        console.out.print(
            f"{render.format_machine(build.machine, args)}/"
            f"{render.format_build_number(build.number)}"
        )
        console.out.print(gbp.logs(build))
        sep = "---\n"

    return 0
