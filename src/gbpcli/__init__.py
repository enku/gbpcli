"""Command Line interface for Gentoo Build Publisher"""
import argparse
import datetime
import os
import sys
from dataclasses import dataclass
from enum import IntEnum
from importlib.metadata import entry_points
from typing import Any, Optional

import requests
import rich.console
import yarl

from gbpcli import queries

from . import queries

LOCAL_TIMEZONE = datetime.datetime.now().astimezone().tzinfo
DEFAULT_URL = os.getenv("BUILD_PUBLISHER_URL", "https://gbp/")


class APIError(Exception):
    """When an error is returned by the REST API"""

    def __init__(self, errors, data) -> None:
        super().__init__(errors)
        self.data = data


@dataclass
class BuildInfo:
    """Metatada about a Build

    Retrieved from the API.
    """

    keep: bool
    note: Optional[str]
    published: bool
    submitted: datetime.datetime
    completed: Optional[datetime.datetime] = None
    built: Optional[datetime.datetime] = None


@dataclass
class Package:
    """A (binary) package"""

    cpv: str


@dataclass
class Build:
    """A GBP Build"""

    machine: str
    number: int
    info: Optional[BuildInfo] = None
    packages_built: Optional[list[Package]] = None

    @property
    def id(self) -> str:  # pylint: disable=invalid-name
        """Return the GBP build id"""
        return f"{self.machine}.{self.number}"

    @classmethod
    def from_id(cls, build_id: str, **kwargs):
        """Create from GBP build id"""
        parts = build_id.partition(".")

        return cls(machine=parts[0], number=int(parts[2]), **kwargs)


class Status(IntEnum):
    """Diff status"""

    REMOVED = -1
    CHANGED = 0
    ADDED = 1


@dataclass
class Change:
    """Item in a diff"""

    item: str
    status: Status


class GBP:
    """Python wrapper for the Gentoo Build Publisher API"""

    headers = {"Accept-Encoding": "gzip, deflate"}

    def __init__(self, url: str, exit_gracefully_on_requests_errors=True) -> None:
        self.url = str(yarl.URL(url) / "graphql")
        self.session = requests.Session()
        self.exit_gracefully_on_requests_errors = exit_gracefully_on_requests_errors

    def query(self, query: str, variables: dict[str, Any] | None = None):
        """Execute the given GraphQL query using the given input variables"""
        json = {"query": query, "variables": variables}

        try:
            response = self.session.post(self.url, json=json, headers=self.headers)
        except requests.exceptions.ConnectionError as error:
            if self.exit_gracefully_on_requests_errors:
                error_message = str(error)
                print(error_message, file=sys.stderr)
                raise SystemExit(-1) from None

            raise

        response.raise_for_status()
        response_json = response.json()
        return response_json.get("data"), response_json.get("errors")

    def machines(self) -> list[tuple[str, int]]:
        """Handler for subcommand"""
        data = self.check(queries.machines)

        return [(i["machine"], i["buildCount"]) for i in data["machines"]]

    def publish(self, build: Build):
        """Publish the given build"""
        self.check(queries.publish, {"id": build.id})

    def pull(self, build: Build):
        """Pull the given build"""
        self.check(queries.pull, {"id": build.id})

    def latest(self, machine: str) -> Optional[Build]:
        """Return the latest build for machine

        Return None if there are no builds for the given machine
        """
        data = self.check(queries.latest, dict(machine=machine))
        latest = data["latest"]

        if latest is None:
            return None

        build_id = data["latest"]["id"]
        return Build.from_id(build_id)

    def builds(self, machine: str, with_packages: bool = False) -> list[Build]:
        """Return a list of Builds for the given machine

        If `with_packages` is True, also include the list of packages for the builds
        """
        query = queries.builds_with_packages if with_packages else queries.builds
        data = self.query(query, dict(machine=machine))[0]
        builds = data["builds"]
        builds.reverse()

        return [self.api_to_build(i) for i in builds]

    def diff(
        self, machine: str, left: int, right: int
    ) -> tuple[Build, Build, list[Change]]:
        """Return difference between two builds"""
        variables = {"left": f"{machine}.{left}", "right": f"{machine}.{right}"}
        data = self.check(queries.diff, variables)

        return (
            self.api_to_build(data["diff"]["left"]),
            self.api_to_build(data["diff"]["right"]),
            [
                Change(item=i["item"], status=getattr(Status, i["status"]))
                for i in data["diff"]["items"]
            ],
        )

    def logs(self, build: Build) -> Optional[str]:
        """Return logs for the given Build"""
        data = self.check(queries.logs, {"id": build.id})
        build = data["build"]

        if build is None:
            return None

        return data["build"]["logs"]

    def get_build_info(self, build: Build) -> Optional[Build]:
        """Return build with info gained from the GBP API"""
        data, errors = self.query(queries.build, {"id": build.id})
        build = data["build"]

        if build is None:
            if errors:
                raise APIError(errors, data)
            return None

        return self.api_to_build(data["build"])

    def build(self, machine: str) -> str:
        """Schedule a build"""
        response = self.check(queries.schedule_build, dict(machine=machine))
        return response["scheduleBuild"]

    def packages(self, build: Build) -> Optional[list[str]]:
        """Return the list of packages for a build"""
        data = self.check(queries.packages, {"id": build.id})
        return data["build"]["packages"]

    def keep(self, build: Build):
        """Mark a build as kept"""
        return self.check(queries.keep_build, {"id": build.id})["keepBuild"]

    def release(self, build: Build):
        """Unmark a build as kept"""
        return self.check(queries.release_build, {"id": build.id})["releaseBuild"]

    def create_note(self, build: Build, note: Optional[str]):
        """Create or delete note for the given build.

        If note is None, the note is deleted (if it exists).
        """
        return self.check(queries.create_note, {"id": build.id, "note": note})[
            "createNote"
        ]

    def search_notes(self, machine: str, key: str) -> list[Build]:
        """Search buids for the given machine name for notes containing key.

        Return a list of Builds who's notes match the (case-insensitive) string.
        """
        query = queries.search_notes

        response = self.check(query, {"machine": machine, "key": key})
        builds = response["searchNotes"]

        return [self.api_to_build(i) for i in builds]

    @staticmethod
    def api_to_build(api_response) -> Build:
        """Return a Build with BuildInfo given the response from the API"""
        completed = api_response.get("completed")
        submitted = api_response["submitted"]
        fromisoformat = datetime.datetime.fromisoformat
        built = api_response.get("built")

        if api_response.get("packagesBuilt", None) is None:
            packages_built = None
        else:
            packages_built = [
                Package(cpv=i["cpv"]) for i in api_response["packagesBuilt"]
            ]

        return Build.from_id(
            api_response["id"],
            info=BuildInfo(
                api_response.get("keep"),
                published=api_response.get("published"),
                note=api_response.get("notes"),
                submitted=fromisoformat(submitted),
                completed=fromisoformat(completed) if completed is not None else None,
                built=fromisoformat(built) if built is not None else None,
            ),
            packages_built=packages_built,
        )

    def check(self, query: str, variables: dict[str, Any] = None) -> dict:
        """Run query and raise exception if there are errors"""
        data, errors = self.query(query, variables)

        if errors:
            raise APIError(errors, data)
        return data


def build_parser() -> argparse.ArgumentParser:
    """Set command-line arguments"""
    parser = argparse.ArgumentParser(prog="gbp")
    parser.add_argument("--url", type=str, help="GBP url", default=DEFAULT_URL)
    parser.add_argument(
        "--color",
        metavar="WHEN",
        choices=["never", "always", "auto"],
        default="auto",
        help="color output",
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
        module.parse_args(subparser)
        subparser.set_defaults(func=module.handler)

    return parser


def main(argv: list[str] | None = None) -> int:
    """Main entry point"""
    if argv is None:
        argv = sys.argv[1:]

    parser = build_parser()

    args = parser.parse_args(argv)

    if not hasattr(args, "func"):
        parser.print_help(file=sys.stderr)
        return 1

    gbp = GBP(args.url)

    force_terminal = {"always": True, "never": False}.get(args.color, None)
    console = rich.console.Console(
        force_terminal=force_terminal, color_system="auto", highlight=False
    )

    try:
        return args.func(args, gbp, console)
    except (APIError, requests.HTTPError) as error:
        print(str(error), file=sys.stderr)

        return 1
