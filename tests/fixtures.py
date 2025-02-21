"""Unittest fixtures"""

# pylint: disable=missing-docstring

import os
from typing import Any
from unittest import mock

import gbp_testkit.fixtures as testkit
from unittest_fixtures import FixtureContext, Fixtures, fixture

from gbpcli import GBP
from gbpcli.config import AuthDict

console = testkit.console
tmpdir = testkit.tmpdir


@fixture("tmpdir")
def environ(
    options: dict[str, str] | None, fixtures: Fixtures
) -> FixtureContext[dict[str, str]]:
    options = options or {}
    mock_environ = {
        **next(testkit.environ(options, fixtures), {}),
        "BUILD_PUBLISHER_API_KEY_ENABLE": "no",
        "BUILD_PUBLISHER_JENKINS_BASE_URL": "https://jenkins.invalid/",
        "BUILD_PUBLISHER_RECORDS_BACKEND": "memory",
        "BUILD_PUBLISHER_STORAGE_PATH": str(fixtures.tmpdir / "gbp"),
        "BUILD_PUBLISHER_WORKER_BACKEND": "sync",
        "BUILD_PUBLISHER_WORKER_THREAD_WAIT": "yes",
        **options,
    }
    with mock.patch.dict(os.environ, mock_environ):
        yield mock_environ


@fixture()
def gbp(options: dict[str, Any] | None, _fixtures: Fixtures) -> GBP:
    """Return a GBP instance with a mock session attribute"""
    # pylint: disable=protected-access
    options = options or {}
    url = options.get("url", "http://test.invalid/")
    auth: AuthDict | None = options.get("auth", None)
    _gbp = GBP(url, auth=auth)
    headers = _gbp.query._session.headers
    _gbp.query._session = mock.Mock()
    _gbp.query._session.headers = headers

    return _gbp


@fixture("tmpdir")
def user_config_dir(_options: None, fixtures: Fixtures):
    with mock.patch(
        "gbpcli.platformdirs.user_config_dir", return_value=fixtures.tmpdir
    ) as patch:
        yield patch
