"""Utility functions"""

import argparse
import datetime as dt
import os
from pathlib import Path
from typing import Any, Iterable, cast

from dotenv import load_dotenv
from rich.table import Table

from gbpcli import GBP
from gbpcli.types import Build

# This is the datetime of the first git commit of gentoo-build-publisher
EPOCH = dt.datetime.fromtimestamp(1616266641, tz=dt.UTC)

DEFAULT_SERVER_CONF = "/etc/gentoo-build-publisher.conf"
TAG_SYM = "@"

ColumnData = Iterable[tuple[str, dict[str, Any]]]


class ResolveBuildError(SystemExit):
    """Exception raised when a build id cannot be resolved

    Note this is a subclass of SystemExit, and therefore not a subclass of
    Exception and therefore will not be caught by "except Exception"
    """


def resolve_build_id(machine: str, build_id: str | None, gbp: GBP) -> Build:
    """Resolve build ids, tags, and optional numbers into a Build object

    If there is an issue finding/calculating the build, then ResolveBuildError, which a
    subclass of SystemExit.
    """
    build = None

    if build_id is None:
        if not (build := gbp.latest(machine)):
            raise ResolveBuildError(f"No builds for {machine}")
        return build

    if build_id.startswith(TAG_SYM):
        tag = build_id[1:]
        if not (build := gbp.resolve_tag(machine, tag)):
            raise ResolveBuildError(f"No such tag for {machine}: {tag}")
        return build

    if build_id.isdigit():
        return Build(machine=machine, number=int(build_id))

    raise ResolveBuildError(f"Invalid build ID: {build_id}")


def get_my_machines_from_args(args: argparse.Namespace) -> list[str]:
    """Return the list of "my machines" attached to parsed args

    If There are none, return an empty list.
    """
    try:
        return cast(list[str], args.my_machines.split())
    except AttributeError:
        return []


def load_env(path: str | Path = DEFAULT_SERVER_CONF) -> bool:
    """Silently load the server config into the environment

    Contents of the file are loaded as environment variables. Return True.

    If the path does not exist or is not readable. Return False
    """
    if not (os.path.exists(path) and os.access(path, os.R_OK)):
        return False

    load_dotenv(path)

    return True


def add_columns(table: Table, data: ColumnData) -> None:
    """Add the given ColumnData to the given table"""
    for header, kwargs in data:
        kwargs = kwargs.copy()
        kwargs.setdefault("header_style", "header")
        table.add_column(header, **kwargs)
