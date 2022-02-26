"""Utility functions"""
import datetime
import io
from functools import partial
from typing import Literal, Optional

from gbpcli import LOCAL_TIMEZONE, Build

JSON_CONTENT_TYPE = "application/json"


def timestr(
    timestamp: datetime.datetime, timezone: Optional[datetime.tzinfo] = None
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
    fprint(f"Build: {build.machine}/{build.number}")
    submitted = timestr(build.info.submitted)
    fprint(f"Submitted: {submitted}")

    assert build.info.completed is not None

    completed = timestr(build.info.completed)
    fprint(f"Completed: {completed}")

    fprint(f"Published: {yesno(build.info.published)}")
    fprint(f"Keep: {yesno(build.info.keep)}")
    fprint("Packages-built:", end="")

    if packages := build.packages_built:
        fprint()

        for package in packages:
            fprint(f"\t{package.cpv}")
    else:
        fprint(" None")

    if note := build.info.note:
        fprint()
        lines = note.split("\n")

        for line in lines:
            fprint(line)

    fprint()
    return myio.getvalue()
