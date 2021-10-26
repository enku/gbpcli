"""Utility functions"""
import datetime
import io
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

    print(f"Build: {build.name}/{build.number}", file=myio)
    submitted = timestr(build.info.submitted)
    print(f"Submitted: {submitted}", file=myio)

    assert build.info.completed is not None

    completed = timestr(build.info.completed)
    print(f"Completed: {completed}", file=myio)

    print(f"Published: {yesno(build.info.published)}", file=myio)
    print(f"Keep: {yesno(build.info.keep)}", file=myio)

    if note := build.info.note:
        print("", file=myio)
        lines = note.split("\n")

        for line in lines:
            print(f"    {line}", file=myio)

    return myio.getvalue()
