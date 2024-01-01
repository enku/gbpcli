"""Subcommands for gbpcli

A "subcommand" for gbpcli is a Python module that has the following interface:

    There must be a function named "handler" with the following signature::

        def handler(
            args: argparse.Namespace,
            gbp: gbpcli.GBP,
            console: gbpcli.Console,
        ) -> int:

    The handler is the function called from the cli to handle the subcommand. It is
    passed the command-line arguments (args), a GBP interface to a Gentoo Build
    Publisher instance, a rich Console instant for display purposes and errorf for
    printing error messages.

    There must also be a "parse_args" function with the following signature::

        def parse_args(parser: argparse.ArgumentParser) -> Any:

    The parse_args is called by the cli. It is responsible for creating the subcommand's
    command-line arguments.  In actuality is it passed a sub-parser instance.
"""
import argparse

from gbpcli.subcommands import completers as comp


def make_searchable(parser: argparse.ArgumentParser) -> None:
    """Set common search-like command-line arguments"""
    comp.set(
        parser.add_argument("machine", metavar="MACHINE", help="name of the machine"),
        comp.machines,
    )
    parser.add_argument(
        "--search",
        "-s",
        action="store_true",
        default=False,
        help="Search builds for the given text.",
    )
    comp.set(
        parser.add_argument("number", metavar="KEY|NUMBER", help="build number"),
        comp.build_ids,
    )
