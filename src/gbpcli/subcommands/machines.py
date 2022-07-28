"""List machines with builds"""
import argparse

from rich.console import Console

from gbpcli import GBP


def handler(_args: argparse.Namespace, gbp: GBP, console: Console) -> int:
    """Handler for machines subcommand"""
    for machine, builds in gbp.machines():
        console.print(f"[bold]{machine:15}[/bold] {builds:>3}")

    return 0


def parse_args(parser: argparse.ArgumentParser) -> None:
    """Set subcommand arguments"""
    parser.set_defaults(handler=handler)
