"""Utility functions"""
import argparse
from typing import Optional

from gbpcli import GBP, Build

TAG_SYM = "@"


class ResolveBuildError(SystemExit):
    """Exception raised when a build id cannot be resolved

    Note this is a subclass of SystemExit, and therefore not a subclass of
    Exception and therefore will not be caught by "except Exception"
    """


def resolve_build_id(machine: str, build_id: Optional[str], gbp: GBP) -> Build:
    """Resolve build ids, tags, and optional numbers into a Build object

    If there is an finding/calculating the build, then ResolveBuildError, which a
    subclass of SystemExit.
    """
    build = None

    if build_id is None:
        build = gbp.latest(machine)
        if not build:
            raise ResolveBuildError(f"No builds for {machine}")
    elif build_id.startswith(TAG_SYM):
        tag = build_id[1:]
        build = gbp.resolve_tag(machine, tag)
        if not build:
            raise ResolveBuildError(f"No such tag for {machine}: {tag}")
    elif build_id.isdigit():
        build = Build(machine, int(build_id))
    else:
        raise ResolveBuildError(f"Invalid build ID: {build_id}")

    return build


def get_my_machines_from_args(args: argparse.Namespace) -> list[str]:
    """Return the list of "my machines" attached to parsed args

    If There are no return an empty list.
    """
    try:
        return args.my_machines.split()
    except AttributeError:
        return []
