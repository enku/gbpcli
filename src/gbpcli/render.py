"""Utilties for rendering output"""
from __future__ import annotations

import argparse
import datetime as dt
import io
from functools import partial
from typing import Literal

from gbpcli import Build, utils

LOCAL_TIMEZONE = dt.datetime.now().astimezone().tzinfo


def yesno(value: bool) -> Literal["yes", "no"]:
    """Convert bool value to 'yes' or 'no'"""
    if value:
        return "yes"

    return "no"


def timestr(timestamp: dt.datetime, timezone: dt.tzinfo | None = None) -> str:
    """Humanize JSON timestamp string"""
    timezone = timezone or LOCAL_TIMEZONE
    dt_obj = timestamp.astimezone(timezone)

    return dt_obj.strftime("%c %z")


def styled_yes(yes_or_no: str) -> str:
    """Like yesno() but yes's are wrapped in green"""
    return f"[{yes_or_no}]{yes_or_no}[/{yes_or_no}]"


def build_to_str(build: Build) -> str:
    """Return Build(Info) as a string

    `build` must have a non-None info struct.
    """
    if build.info is None:
        raise ValueError("Build contains no `.info")

    myio = io.StringIO()

    fprint = partial(print, file=myio)
    fprint(f"[bold]Build:[/bold] [blue]{build.machine}/{build.number}[/blue]")

    if build.info.built is not None:
        built = timestr(build.info.built)
        fprint(f"[bold]BuildDate:[/bold] {built}")

    submitted = timestr(build.info.submitted)
    fprint(f"[bold]Submitted:[/bold] {submitted}")

    completed = timestr(build.info.completed) if build.info.completed else "no"
    fprint(f"[bold]Completed:[/bold] {completed}")

    fprint(f"[bold]Published:[/bold] {yesno(build.info.published)}")
    fprint(f"[bold]Keep:[/bold] {yesno(build.info.keep)}")
    fprint(f"[bold]Tags:[/bold] {' '.join(build.info.tags)}")
    fprint("[bold]Packages-built:[/bold]", end="")

    if packages := build.packages_built:
        fprint()

        for package in packages:
            fprint(f"    {package.cpv}")
    else:
        fprint(" None" if build.info.completed else " Unknown")

    if note := build.info.note:
        fprint()
        lines = note.split("\n")

        for line in lines:
            fprint(line)

    fprint()
    return myio.getvalue()


## format_**() functions below return rich.Console-enabled format strings
def format_flags(build: Build) -> str:
    """Return build (info) as a string of rich'ly formatted symbols.

    For example:

        "* P  "

    Which means that the build has packages built and is published.
    """
    assert build.info is not None

    return (
        f"{'[package]*[/package]' if build.packages_built else ' '}"
        f"{'[keep]K[/keep]' if build.info.keep else ' '}"
        f"{'[published]P[/published]' if build.info.published else ' '}"
        f"{'[note_flag]N[/note_flag]' if build.info.note else ' '}"
    )


def format_build_number(number: int) -> str:
    """Return the (build) number rich'ly formatted"""
    return f"[build_id]{number}[/build_id]"


def format_timestamp(timestamp: dt.datetime) -> str:
    """Return the timestamp rich'ly formatted"""
    return f"[timestamp]{timestamp.strftime('%x %X')}[/timestamp]"


def format_tags(tags: list[str]) -> str:
    """Return the list of build tags rich'ly formatted"""
    tag_list = [f"@{tag}" for tag in tags]

    return f"[tag]{' '.join(tag_list)}[/tag]"


def format_machine(machine: str, args: argparse.Namespace) -> str:
    """Format the given machine name for rich output

    If the given machine is given in the `my_machines` argument then it will have
    special styling.
    """
    pre, post = "", ""

    if machine in utils.get_my_machines_from_args(args):
        pre = "[mymachine]"
        post = "[/mymachine]"

    return f"[machine]{pre}{machine}{post}[/machine]"
