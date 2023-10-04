"""Command Line interface for Gentoo Build Publisher"""
from __future__ import annotations

import argparse
import datetime
import os
import sys
import warnings
from dataclasses import dataclass
from enum import Enum, IntEnum
from importlib.metadata import entry_points, version
from typing import IO, Any, Callable, TypeAlias, TypeVar

import requests
import rich.console
import yarl
from rich.theme import Theme

from gbpcli import graphql, theme

COLOR_CHOICES = {"always": True, "never": False, "auto": None}
DEFAULT_URL = os.getenv("BUILD_PUBLISHER_URL", "http://localhost/")


@dataclass(frozen=True)
class BuildInfo:
    """Metatada about a Build

    Retrieved from the API.
    """

    keep: bool
    note: str | None
    published: bool
    tags: list[str]
    submitted: datetime.datetime
    completed: datetime.datetime | None = None
    built: datetime.datetime | None = None


@dataclass(frozen=True)
class Package:
    """A (binary) package"""

    cpv: str
    build_time: datetime.datetime


T = TypeVar("T", bound="Build")


@dataclass(frozen=True)
class Build:
    """A GBP Build"""

    machine: str
    number: int
    info: BuildInfo | None = None
    packages_built: list[Package] | None = None

    @property
    def id(self) -> str:  # pylint: disable=invalid-name
        """Return the GBP build id"""
        return f"{self.machine}.{self.number}"

    @classmethod
    def from_id(cls: type[T], build_id: str, **kwargs) -> T:
        """Create from GBP build id"""
        parts = build_id.partition(".")

        return cls(machine=parts[0], number=int(parts[2]), **kwargs)

    @classmethod
    def from_api_response(cls: type[T], api_response) -> T:
        """Return a Build with BuildInfo given the response from the API"""
        completed = api_response.get("completed")
        submitted = api_response["submitted"]
        fromisoformat = datetime.datetime.fromisoformat
        built = api_response.get("built")

        packages_built = (
            None
            if (packages := api_response.get("packagesBuilt", None)) is None
            else [
                Package(
                    cpv=i["cpv"],
                    build_time=datetime.datetime.fromtimestamp(i.get("buildTime", 0)),
                )
                for i in packages
            ]
        )

        return cls.from_id(
            api_response["id"],
            info=BuildInfo(
                api_response.get("keep"),
                published=api_response.get("published"),
                tags=api_response.get("tags"),
                note=api_response.get("notes"),
                submitted=fromisoformat(submitted),
                completed=fromisoformat(completed) if completed is not None else None,
                built=fromisoformat(built) if built is not None else None,
            ),
            packages_built=packages_built,
        )


class Status(IntEnum):
    """Diff status"""

    REMOVED = -1
    CHANGED = 0
    ADDED = 1


class SearchField(Enum):
    """Search fields"""

    # pylint: disable=invalid-name

    logs = "LOGS"
    notes = "NOTES"


@dataclass
class Change:
    """Item in a diff"""

    item: str
    status: Status


@dataclass(frozen=True)
class Console:
    """Output sinks for handlers"""

    out: rich.console.Console
    err: rich.console.Console


class GBP:
    """Python wrapper for the Gentoo Build Publisher API"""

    def __init__(self, url: str, distribution: str = "gbpcli") -> None:
        self.query = graphql.Queries(
            yarl.URL(url) / "graphql", distribution=distribution
        )

    def machines(self) -> list[tuple[str, int, dict]]:
        """Handler for subcommand"""
        data = graphql.check(self.query.machines())

        return [
            (i["machine"], i["buildCount"], i["latestBuild"]) for i in data["machines"]
        ]

    def machine_names(self) -> list[str]:
        """Return the list of machine names

        Machines having builds.
        """
        machines = graphql.check(self.query.machine_names())["machines"]

        return [machine["machine"] for machine in machines]

    def publish(self, build: Build) -> None:
        """Publish the given build"""
        graphql.check(self.query.publish(id=build.id))

    def pull(self, build: Build) -> None:
        """Pull the given build"""
        graphql.check(self.query.pull(id=build.id))

    def latest(self, machine: str) -> Build | None:
        """Return the latest build for machine

        Return None if there are no builds for the given machine
        """
        data = graphql.check(self.query.latest(machine=machine))

        if data["latest"] is None:
            return None

        build_id = data["latest"]["id"]
        return Build.from_id(build_id)

    def resolve_tag(self, machine: str, tag: str) -> Build | None:
        """Return the build of the given machine & tag"""
        data = graphql.check(self.query.resolve_tag(machine=machine, tag=tag))[
            "resolveBuildTag"
        ]

        if data is None:
            return None

        build_id = data["id"]

        return Build.from_id(build_id)

    def builds(self, machine: str, with_packages: bool = False) -> list[Build]:
        """Return a list of Builds for the given machine

        If `with_packages` is True, also include the list of packages for the builds
        """
        query = self.query.builds_with_packages if with_packages else self.query.builds
        data = query(machine=machine)[0]
        builds = data["builds"]
        builds.reverse()

        return [Build.from_api_response(i) for i in builds]

    def diff(
        self, machine: str, left: int, right: int
    ) -> tuple[Build, Build, list[Change]]:
        """Return difference between two builds"""
        data = graphql.check(
            self.query.diff(left=f"{machine}.{left}", right=f"{machine}.{right}")
        )

        return (
            Build.from_api_response(data["diff"]["left"]),
            Build.from_api_response(data["diff"]["right"]),
            [
                Change(item=i["item"], status=getattr(Status, i["status"]))
                for i in data["diff"]["items"]
            ],
        )

    def logs(self, build: Build) -> str | None:
        """Return logs for the given Build"""
        data = graphql.check(self.query.logs(id=build.id))

        return None if data["build"] is None else data["build"]["logs"]

    def get_build_info(self, build: Build) -> Build | None:
        """Return build with info gained from the GBP API"""
        data, errors = self.query.build(id=build.id)

        if (build := data["build"]) is None:
            if errors:
                raise graphql.APIError(errors, data)
            return None

        return Build.from_api_response(build)

    def build(self, machine: str) -> str:
        """Schedule a build"""
        response = graphql.check(self.query.schedule_build(machine=machine))
        return response["scheduleBuild"]

    def packages(self, build: Build) -> list[str] | None:
        """Return the list of packages for a build"""
        data = graphql.check(self.query.packages(id=build.id))
        return data["build"]["packages"]

    def keep(self, build: Build) -> dict[str, bool]:
        """Mark a build as kept"""
        return graphql.check(self.query.keep_build(id=build.id))["keepBuild"]

    def release(self, build: Build) -> dict[str, bool]:
        """Unmark a build as kept"""
        return graphql.check(self.query.release_build(id=build.id))["releaseBuild"]

    def create_note(self, build: Build, note: str | None) -> dict[str, str]:
        """Create or delete note for the given build.

        If note is None, the note is deleted (if it exists).
        """
        return graphql.check(self.query.create_note(id=build.id, note=note))[
            "createNote"
        ]

    def search(self, machine: str, field: SearchField, key: str) -> list[Build]:
        """Search builds for the given machine name in fields containing key.

        Return a list of Builds who's given field match the (case-insensitive) string.
        """
        response = graphql.check(
            self.query.search(machine=machine, field=field.value, key=key)
        )
        builds = response["search"]

        return [Build.from_api_response(i) for i in builds]

    def search_notes(self, machine: str, key: str) -> list[Build]:
        """Search builds for the given machine name for notes containing key.

        This method is deprecated. Use search() instead.
        """
        message = "This method is deprecated. Use search() instead"
        warnings.warn(message, DeprecationWarning, stacklevel=2)

        return self.search(machine, SearchField.notes, key)

    def tag(self, build: Build, tag: str) -> None:
        """Add the given tag to the build"""
        graphql.check(self.query.tag_build(id=build.id, tag=tag))

    def untag(self, machine: str, tag: str) -> None:
        """Remove the tag from the given machine"""
        graphql.check(self.query.untag_build(machine=machine, tag=tag))


def build_parser() -> argparse.ArgumentParser:
    """Set command-line arguments"""
    usage = "Command-line interface to Gentoo Build Publisher\n\nCommands:\n\n"
    parser = argparse.ArgumentParser(prog="gbp")
    parser.add_argument(
        "--version", action="version", version=f"gbpcli {version('gbpcli')}"
    )
    parser.add_argument("--url", type=str, help="GBP url", default=DEFAULT_URL)
    parser.add_argument(
        "--color",
        metavar="WHEN",
        choices=COLOR_CHOICES,
        default="auto",
        help=f"colorize output {tuple(COLOR_CHOICES)}",
    )
    parser.add_argument(
        "--my-machines",
        default=os.getenv("GBPCLI_MYMACHINES", ""),
        help=(
            "whitespace-delimited list of machine names to filter on "
            "when using the --mine argument. Typically one would instead use "
            "the GBPCLI_MYMACHINES environment variable."
        ),
    )
    subparsers = parser.add_subparsers()

    try:
        eps = entry_points().select(group="gbpcli.subcommands")
    except AttributeError:
        eps = entry_points()["gbpcli.subcommands"]

    for entry_point in eps:
        module = entry_point.load()
        subparser = subparsers.add_parser(
            entry_point.name,
            description=module.__doc__,
            formatter_class=argparse.RawTextHelpFormatter,
        )
        usage = f"{usage}  * {entry_point.name} - {module.handler.__doc__}\n"
        module.parse_args(subparser)
        subparser.set_defaults(func=module.handler)

    parser.usage = usage

    return parser


def get_arguments(argv: list[str] | None = None) -> argparse.Namespace:
    """Return command line arguments given the argv

    This method ensures that args.func is defined as it's mandatory for calling
    subcommands. If there are none the help message is printed to stderr and SystemExit
    is raised.
    """
    argv = argv if argv is not None else sys.argv[1:]
    parser = build_parser()
    args = parser.parse_args(argv)

    # ensure we have a "func" target
    if not hasattr(args, "func"):
        parser.print_help(file=sys.stderr)
        raise SystemExit(1)

    return args


def get_console(
    force_terminal: bool | None, color_map: theme.ColorMap | None = None
) -> Console:
    """Return a rich.Console instance

    If force_terminal is true, force a tty on the console.
    If the ColorMap is given this is used as the Console theme
    """
    return Console(
        out=rich.console.Console(
            force_terminal=force_terminal,
            color_system="auto",
            highlight=False,
            theme=Theme(color_map or theme.DEFAULT_THEME),
        ),
        err=rich.console.Console(file=sys.stderr),
    )


def main(argv: list[str] | None = None) -> int:
    """Main entry point"""
    args = get_arguments(argv)
    color_map = theme.get_colormap_from_string(os.getenv("GBPCLI_COLORS", ""))
    console = get_console(COLOR_CHOICES[args.color], color_map)

    try:
        return args.func(args, GBP(args.url), console)
    except (graphql.APIError, requests.HTTPError, requests.ConnectionError) as error:
        console.err.print(str(error))
        return 1
