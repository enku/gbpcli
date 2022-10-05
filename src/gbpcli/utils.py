"""Utility functions"""
import datetime
import io
import sys
from functools import partial
from typing import Literal, Optional

from gbpcli import GBP, LOCAL_TIMEZONE, Build

JSON_CONTENT_TYPE = "application/json"
TAG_SYM = "@"


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


def styled_yes(value: bool) -> str:
    """Like yesno() but yes's are wrapped in green"""
    yes_or_no = yesno(value)

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


def resolve_build_id(
    machine: str, build_id: Optional[str], gbp: GBP, abort_on_error: bool = True
) -> Build:
    """Resolve build ids, tags, and optional numbers into a Build object

    If abort_on_error is True and there is an error finding/calculating the build, then
    an error is printed to sys.stderr and SystemExit is raised.
    """
    build = None
    error = SystemExit(1)

    if build_id is None:
        build = gbp.latest(machine)
        if not build and abort_on_error:
            print(f"No builds for {machine}", file=sys.stderr)
            raise error
    elif build_id.startswith(TAG_SYM):
        tag = build_id[1:]
        build = gbp.resolve_tag(machine, tag)
        if not build and abort_on_error:
            print(f"No such tag for {machine}: {tag}", file=sys.stderr)
            raise error
    elif build_id.isdigit():
        build = Build(machine, int(build_id))
    elif abort_on_error:
        print(f"Invalid build ID: {build_id}", file=sys.stderr)
        raise error

    if build is None:
        raise ValueError(f"Invalid build ID: {build_id}")

    return build
