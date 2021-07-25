"""Command Line interface for Gentoo Build Publisher"""
import argparse
import datetime
import os
import sys
from dataclasses import dataclass
from enum import IntEnum
from importlib.metadata import entry_points
from typing import List, Optional, Tuple

import requests
import yarl

JSON_CONTENT_TYPE = "application/json"
LOCAL_TIMEZONE = datetime.datetime.now().astimezone().tzinfo
DEFAULT_URL = os.getenv("BUILD_PUBLISHER_URL", "https://gbp/")


class NotFound(Exception):
    """Raised when a build does not exist"""


class APIError(Exception):
    """When an error is returned by the REST API"""

    def __init__(self, msg, json):
        super().__init__(msg)
        self.json = json


class UnexpectedResponseError(Exception):
    """Got an unexpected response from the server"""

    def __init__(self, response: requests.Response):
        super().__init__("Unexpected server response")
        self.response = response


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


@dataclass
class Build:
    """A GBP Build"""

    name: str
    number: int
    info: Optional[BuildInfo] = None


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

    def __init__(self, url: str):
        self.url = yarl.URL(url)
        self.session = requests.Session()

    def machines(self) -> List[Tuple[str, int]]:
        """Handler for subcommand"""
        url = self.url / "api/machines/"
        response = self.check(self.session.get(str(url)))

        return [(i["name"], i["builds"]) for i in response["machines"]]

    def publish(self, build: Build):
        """Publish the given build"""
        url = self.url / f"api/builds/{build.name}/{build.number}/publish"
        self.check(self.session.post(str(url)))

    def latest(self, machine: str) -> Build:
        """Return the latest build for machine

        Return None if there are no builds for the given machine
        """
        url = self.url / f"api/builds/{machine}/latest"
        response = self.check(self.session.get(str(url)))

        number = response["number"]

        return Build(name=machine, number=number)

    def builds(self, machine: str) -> List[Build]:
        """Return a list of Builds for the given machine"""
        url = self.url / f"api/builds/{machine}/"
        response = self.check(self.session.get(str(url)))

        return [self.api_to_build(i) for i in response["builds"]]

    def diff(
        self, machine: str, left: int, right: int
    ) -> Tuple[Build, Build, List[Change]]:
        """Return difference between two builds"""
        url = self.url / f"api/builds/{machine}/diff/{left}/{right}"
        response = self.check(self.session.get(str(url)))

        return (
            self.api_to_build(response["diff"]["builds"][0]),
            self.api_to_build(response["diff"]["builds"][1]),
            [Change(item=i[1], status=Status(i[0])) for i in response["diff"]["items"]],
        )

    def logs(self, build: Build) -> str:
        """Return logs for the given Build"""
        url = self.url / f"api/builds/{build.name}/{build.number}/log"
        response = self.session.get(str(url))

        if response.status_code == 404:
            raise NotFound()

        return response.text

    def get_build_info(self, build: Build) -> Build:
        """Return build with info gained from the GBP API"""
        url = self.url / f"api/builds/{build.name}/{build.number}"

        response = self.check(self.session.get(str(url)))

        return self.api_to_build(response)

    @staticmethod
    def api_to_build(api_response) -> Build:
        """Return a Build with BuildInfo given the response from the API"""
        return Build(
            name=api_response["name"],
            number=api_response["number"],
            info=BuildInfo(
                api_response["db"]["keep"],
                published=api_response["storage"]["published"],
                note=api_response["db"]["note"],
                submitted=datetime.datetime.fromisoformat(
                    api_response["db"]["submitted"]
                ),
                completed=datetime.datetime.fromisoformat(
                    api_response["db"]["completed"]
                ),
            ),
        )

    @staticmethod
    def check(response: requests.Response, is_json: bool = True):
        """Check the requests response.

        If the status code 404, raise NotFound
        """
        if response.status_code == 404:
            raise NotFound

        if is_json:
            if (
                response.headers.get("content-type", "").partition(";")[0]
                != JSON_CONTENT_TYPE
            ):
                raise UnexpectedResponseError(response)

            data = response.json()

            if error := data["error"]:
                raise APIError(error, data)

            return data

        return response.content


def build_parser() -> argparse.ArgumentParser:
    """Set command-line arguments"""
    parser = argparse.ArgumentParser(prog="gbp")
    parser.add_argument("--url", type=str, help="GBP url", default=DEFAULT_URL)
    subparsers = parser.add_subparsers()

    for entry_point in entry_points()["gbpcli.subcommands"]:
        module = entry_point.load()
        subparser = subparsers.add_parser(entry_point.name, description=module.__doc__)
        module.parse_args(subparser)
        subparser.set_defaults(func=module.handler)

    return parser


def main(argv=None) -> int:
    """Main entry point"""
    if argv is None:
        argv = sys.argv[1:]

    parser = build_parser()

    args = parser.parse_args(argv)

    if not hasattr(args, "func"):
        parser.print_help(file=sys.stderr)
        return 1

    gbp = GBP(args.url)

    try:
        return args.func(args, gbp)
    except (APIError, UnexpectedResponseError) as error:
        print(str(error), file=sys.stderr)

        return 1
