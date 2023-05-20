"""Display logs for the given build"""
import argparse

from rich.console import Console

from gbpcli import GBP, SearchField, render, utils
from gbpcli.subcommands import make_searchable


def search_logs(gbp: GBP, args: argparse.Namespace, out: Console, err: Console) -> int:
    """--search handler for the notes subcommand"""
    builds = gbp.search(args.machine, SearchField.logs, args.number)

    if not builds:
        err.print("No matches found")
        return 1

    sep = ""
    for build in builds:  # pylint: disable=duplicate-code
        out.print(sep, end="")
        out.print(
            f"{render.format_machine(build.machine, args)}/"
            f"{render.format_build_number(build.number)}"
        )
        out.print(gbp.logs(build))
        sep = "---\n"

    return 0


def handler(args: argparse.Namespace, gbp: GBP, out: Console, err: Console) -> int:
    """Show build logs"""
    if args.search:
        return search_logs(gbp, args, out, err)

    build = utils.resolve_build_id(args.machine, args.number, gbp)
    text = gbp.logs(build)

    if text is None:
        err.print("Not Found")
        return 1

    out.print(text)

    return 0


def parse_args(parser: argparse.ArgumentParser) -> None:
    """Set subcommand arguments"""
    make_searchable(parser)
