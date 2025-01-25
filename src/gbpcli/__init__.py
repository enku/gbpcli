"""Command Line interface for Gentoo Build Publisher"""

# PYTHON_ARGCOMPLETE_OK
from __future__ import annotations

import argparse
import os
import os.path
import sys
import warnings
from importlib.metadata import entry_points, version
from typing import Any, cast

import argcomplete
import platformdirs
import requests
import rich.console
import yarl
from rich.theme import Theme

from gbpcli import config, graphql
from gbpcli.gbp import GBP
from gbpcli.theme import get_theme_from_string
from gbpcli.types import Build, Change, ChangeState, Console, SearchField

COLOR_CHOICES = {"always": True, "never": False, "auto": None}
DEFAULT_URL = os.getenv("BUILD_PUBLISHER_URL", "http://localhost/")


def build_parser(user_config: config.Config) -> argparse.ArgumentParser:
    """Set command-line arguments"""
    usage = "Command-line interface to Gentoo Build Publisher\n\nCommands:\n\n"
    parser = argparse.ArgumentParser(prog="gbp")
    parser.add_argument(
        "--version", action="version", version=f"gbpcli {version('gbpcli')}"
    )
    parser.add_argument(
        "--url", type=str, help="GBP url", default=user_config.url or DEFAULT_URL
    )
    parser.add_argument(
        "--color",
        metavar="WHEN",
        choices=COLOR_CHOICES,
        default="auto",
        help=f"colorize output {tuple(COLOR_CHOICES)}",
    )
    parser.add_argument(
        "--my-machines",
        default=" ".join(user_config.my_machines or [])
        or os.getenv("GBPCLI_MYMACHINES", ""),
        help=(
            "whitespace-delimited list of machine names to filter on "
            "when using the --mine argument. Typically one would instead use "
            "the GBPCLI_MYMACHINES environment variable or the `my_machines`"
            f"setting in {platformdirs.user_config_dir()}/gbpcli.toml"
        ),
    )
    subparsers = parser.add_subparsers()

    eps = entry_points().select(group="gbpcli.subcommands")

    for entry_point in eps:
        module = entry_point.load()
        subparser = subparsers.add_parser(
            entry_point.name,
            description=getattr(module, "HELP", None),
            formatter_class=argparse.RawTextHelpFormatter,
        )
        usage = f"{usage}  * {entry_point.name} - {module.handler.__doc__}\n"
        module.parse_args(subparser)
        subparser.set_defaults(func=module.handler)

    parser.usage = usage

    return parser


def get_arguments(
    user_config: config.Config, argv: list[str] | None = None
) -> argparse.Namespace:
    """Return command line arguments given the argv

    This method ensures that args.func is defined as it's mandatory for calling
    subcommands. If there are none the help message is printed to stderr and SystemExit
    is raised.
    """
    argv = argv if argv is not None else sys.argv[1:]
    parser = build_parser(user_config)
    supress_completer = argcomplete.completers.SuppressCompleter()
    argcomplete.autocomplete(parser, default_completer=supress_completer)
    args = parser.parse_args(argv)
    ensure_args_has_func(args, parser)

    return args


def get_console(force_terminal: bool | None, theme: Theme) -> Console:
    """Return a rich.Console instance

    If force_terminal is true, force a tty on the console.
    If the ColorMap is given this is used as the Console theme
    """
    out = rich.console.Console(
        force_terminal=force_terminal, color_system="auto", highlight=False, theme=theme
    )
    return Console(out=out, err=rich.console.Console(file=sys.stderr))


def get_user_config(filename: str | None = None) -> config.Config:
    """Return Config from the user's"""
    config_dir = platformdirs.user_config_dir()
    user_config_file = filename or os.path.join(config_dir, "gbpcli.toml")

    try:
        with open(user_config_file, "rb") as fp:
            return config.Config.from_file(fp)
    except FileNotFoundError:
        if filename:
            raise
        return config.Config()


def set_environ():
    """Set default environment variables

    These are needed in order to load modules from Gentoo Build Publisher
    """
    os.environ.setdefault("BUILD_PUBLISHER_JENKINS_BASE_URL", "http://jenkins.invalid")
    os.environ.setdefault("BUILD_PUBLISHER_STORAGE_PATH", "__testing__")
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "gbpcli.django_settings")


def ensure_args_has_func(
    args: argparse.Namespace, parser: argparse.ArgumentParser
) -> None:
    """Raise SystemExit if args has no "func" attribute

    Print parser help to stderr before exiting
    """
    if not hasattr(args, "func"):
        parser.print_help(file=sys.stderr)
        raise SystemExit(1)


def main(argv: list[str] | None = None) -> int:
    """Main entry point"""
    set_environ()
    user_config = get_user_config(os.environ.get("GBPCLI_CONFIG"))
    args = get_arguments(user_config, argv)
    theme = get_theme_from_string(os.getenv("GBPCLI_COLORS", ""))
    console = get_console(COLOR_CHOICES[args.color], theme)

    try:
        return cast(int, args.func(args, GBP(args.url, auth=user_config.auth), console))
    except (graphql.APIError, requests.HTTPError, requests.ConnectionError) as error:
        console.err.print(str(error))
        return 1
