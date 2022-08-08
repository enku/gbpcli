"""List builds for the given machines"""
import argparse

from rich.console import Console

from gbpcli import GBP, LOCAL_TIMEZONE


def handler(args: argparse.Namespace, gbp: GBP, console: Console) -> int:
    """Handler for subcommand"""
    builds = gbp.builds(args.machine, with_packages=True)

    for build in builds:
        assert build.info is not None
        timestamp = build.info.submitted.astimezone(LOCAL_TIMEZONE)

        output = (
            "["
            f"{'[magenta]*[/magenta]' if build.packages_built else ' '}"
            f"{'[yellow]K[/yellow]' if build.info.keep else ' '}"
            f"{'[bold green]P[/bold green]' if build.info.published else ' '}"
            f"{'[blue]N[/blue]' if build.info.note else ' '}"
            "]"
            f" [bold]{build.number:>5}[/bold]"
            f" {timestamp.strftime('%x %X')}"
        )
        if build.info.tags:
            tags = [f"@{tag}" for tag in build.info.tags]
            output += f" [yellow]{' '.join(tags)}[/yellow]"

        console.print(output)

    return 0


def parse_args(parser: argparse.ArgumentParser):
    """Set subcommand arguments"""
    parser.add_argument("machine", metavar="MACHINE", help="name of the machine")
