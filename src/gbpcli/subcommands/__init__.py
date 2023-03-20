"""Subcommands for gbpcli

A "subcommand" for gbpcli is a Python module that has the following interface:

    There must be a function named "handler" with the following signature::

        def handler(
            args: argparse.Namespace,
            gbp: gbpcli.GBP,
            console: rich.console.Console,
            errorf: typing.TextIO
        ) -> int:

    The handler is the function called from the cli to handle the subcommand. It is
    passed the command-line arguments (args), a GBP interface to a Gentoo Build
    Publisher instance, a rich Console instant for display purposes and errorf for
    printing error messages.

    There must also be a "parse_args" function with the following signature::

        def parse_args(parser: argparse.ArgumentParser) -> None:

    The parse_args is called by the cli. It is responsible for creating the subcommand's
    command-line arguments.  In actuality is it passed a sub-parser instance.
"""
