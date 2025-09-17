"""Utility functions"""

import argparse
import datetime as dt
import os
import sys
from pathlib import Path
from typing import Any, Iterable, cast

from dotenv import load_dotenv
from rich.table import Table

from gbpcli.gbp import GBP
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
    if build_id is None:
        return latest(machine, gbp)

    if build_id.startswith(TAG_SYM):
        return resolve_tag(machine, build_id[1:], gbp)

    if build_id.isdigit():
        return Build(machine=machine, number=int(build_id))

    raise ResolveBuildError(f"Invalid build ID: {build_id!r}")


def get_my_machines_from_args(args: argparse.Namespace) -> list[str]:
    """Return the list of "my machines" attached to parsed args

    If There are none, return an empty list.
    """
    try:
        return cast(list[str], args.my_machines.split())
    except AttributeError:
        return []


def set_env() -> None:
    """Set default environment variables

    These are needed in order to load modules from Gentoo Build Publisher
    """
    os.environ.setdefault("BUILD_PUBLISHER_JENKINS_BASE_URL", "http://jenkins.invalid")
    os.environ.setdefault("BUILD_PUBLISHER_STORAGE_PATH", "__testing__")
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "gbpcli.django_settings")


def load_env(path: str | Path = DEFAULT_SERVER_CONF) -> bool:
    """Silently load the server config into the environment

    Also re-evaluate sys.path according to PYTHONPATH.

    Contents of the file are loaded as environment variables. Return True.

    If the path does not exist or is not readable. Return False
    """
    if os.environ.get("GBPCLI_DONTLOADSERVERENV", ""):
        return False

    if not (os.path.exists(path) and os.access(path, os.R_OK)):
        return False

    load_dotenv(path, override=True)
    re_path()

    return True


def re_path() -> None:
    """Evaluate PYTHONPATH and set sys.path accordingly"""
    environ = os.environ
    pythonpath = environ.get("PYTHONPATH", "")

    for path in pythonpath.split(os.pathsep):
        if path not in sys.path:
            sys.path.insert(0, path)


def add_columns(table: Table, data: ColumnData) -> None:
    """Add the given ColumnData to the given table"""
    for header, kwargs in data:
        kwargs = kwargs.copy()
        kwargs.setdefault("header_style", "header")
        table.add_column(header, **kwargs)


def latest(machine: str, gbp: GBP) -> Build:
    """Return the latest build for the given machine

    Raise ResolveBuildError if there are no builds
    """
    if not (build := gbp.latest(machine)):
        raise ResolveBuildError(f"No builds for {machine}")

    return build


def resolve_tag(machine: str, tag: str, gbp: GBP) -> Build:
    """Resolves the given tag for the given machine

    `tag` should not start with a `"@"` except for the special `"@"` tag which is
    translated to mean the latest build for the given machine.

    Raise ResolveBuildError if there are no builds with the given tag.
    """
    if tag == "@":
        build = gbp.latest(machine)
        error_msg = f"No builds for {machine}"
    else:
        build = gbp.resolve_tag(machine, tag)
        error_msg = f"No such tag for {machine}: {tag!r}"

    if not build:
        raise ResolveBuildError(error_msg)

    return build
