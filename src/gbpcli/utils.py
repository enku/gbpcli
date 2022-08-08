"""Utility functions"""
import datetime
import io
from functools import partial
from typing import Literal

from gbpcli import LOCAL_TIMEZONE, Build

JSON_CONTENT_TYPE = "application/json"


def timestr(
    timestamp: datetime.datetime, timezone: datetime.tzinfo | None = None
) -> str:
    """Humanize JSON timestamp string"""
    timezone = timezone or LOCAL_TIMEZONE
    dt_obj = timestamp.astimezone(timezone)

    return dt_obj.strftime("%c %z")


def yesno(value: bool) -> Literal["yes", "no"]:
    """Convert bool value to 'yes' or 'no'"""
    if value:
        return "yes"

    return "no"


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

    assert build.info.completed is not None

    completed = timestr(build.info.completed)
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
        fprint(" None")

    if note := build.info.note:
        fprint()
        lines = note.split("\n")

        for line in lines:
            fprint(line)

    fprint()
    return myio.getvalue()
