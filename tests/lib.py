"""Unittest tools"""

# pylint: disable=missing-docstring,protected-access

import datetime as dt
from json import dumps as stringify
from typing import Sequence
from unittest import mock

import gbp_testkit.fixtures as testkit
import requests
from gentoo_build_publisher import publisher
from gentoo_build_publisher.records import BuildRecord
from gentoo_build_publisher.types import Build
from unittest_fixtures import FixtureContext, Fixtures, fixture

NO_JSON = object()


@fixture(testkit.tmpdir)
def user_config_dir(fixtures: Fixtures) -> FixtureContext[mock.Mock]:
    with mock.patch(
        "gbpcli.platformdirs.user_config_dir", return_value=fixtures.tmpdir
    ) as patch:
        yield patch


@fixture(testkit.publisher, testkit.build)
def pulled_build(  # pylint: disable=too-many-arguments
    fixtures: Fixtures,
    *,
    build: Build | None = None,
    built: dt.datetime = dt.datetime(2021, 11, 13, 4, 23, 34, tzinfo=dt.UTC),
    submitted: dt.datetime = dt.datetime(2021, 11, 13, 4, 25, 53, tzinfo=dt.UTC),
    completed: dt.datetime = dt.datetime(2021, 11, 13, 4, 29, 34, tzinfo=dt.UTC),
    packages: Sequence[str] = (),
    note: str | None = None,
    tags: Sequence[str] | None = None,
    logs: str | None = None,
    clear: bool = False,
) -> BuildRecord:
    build = build or fixtures.build
    builder = publisher.jenkins.artifact_builder  # type: ignore

    if clear:
        builder._builds.clear()

    for package in packages:
        builder.build(build, package)

    publisher.pull(build, tags=list(tags) if tags else None)

    return publisher.save(
        publisher.record(build),
        built=built,
        submitted=submitted,
        completed=completed,
        note=note,
        logs=logs,
    )


def http_response(status_code=200, json=NO_JSON, content=None) -> requests.Response:
    """Create a mock requests.Response object"""
    # pylint: disable=protected-access
    if content is None:
        content = b"test"

    response = requests.Response()
    response.status_code = status_code
    response._content = content

    if json is not NO_JSON:
        response._content = stringify(json, sort_keys=True).encode("utf-8")
        response.headers["Content-Type"] = "application/json"

    return response


def create_machine_builds(machine: str, count: int, stop: int):
    for i in range(stop - count + 1, stop + 1):
        publisher.pull(Build(machine=machine, build_id=str(i)))
