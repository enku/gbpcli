"""Utility functions"""
import argparse
import sys
from typing import Optional, TextIO

from gbpcli import GBP, Build

JSON_CONTENT_TYPE = "application/json"
TAG_SYM = "@"


def resolve_build_id(
    machine: str,
    build_id: Optional[str],
    gbp: GBP,
    abort_on_error: bool = True,
    errorf: TextIO = sys.stderr,
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
            print(f"No builds for {machine}", file=errorf)
            raise error
    elif build_id.startswith(TAG_SYM):
        tag = build_id[1:]
        build = gbp.resolve_tag(machine, tag)
        if not build and abort_on_error:
            print(f"No such tag for {machine}: {tag}", file=errorf)
            raise error
    elif build_id.isdigit():
        build = Build(machine, int(build_id))
    elif abort_on_error:
        print(f"Invalid build ID: {build_id}", file=errorf)
        raise error

    if build is None:
        raise ValueError(f"Invalid build ID: {build_id}")

    return build


def get_my_machines_from_args(args: argparse.Namespace) -> list[str]:
    """Return the list of "my machines" attached to parsed args

    If There are no return an empty list.
    """
    try:
        return args.my_machines.split()
    except AttributeError:
        return []
