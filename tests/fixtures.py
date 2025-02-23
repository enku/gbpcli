"""Unittest fixtures"""

# pylint: disable=missing-docstring

import os
from unittest import mock

import gbp_testkit.fixtures as testkit
from unittest_fixtures import FixtureContext, Fixtures, fixture

from gbpcli import GBP
from gbpcli.config import AuthDict

console = testkit.console
tmpdir = testkit.tmpdir


@fixture("tmpdir")
def environ(
    fixtures: Fixtures,
    environ: dict[str, str] | None = None,  # pylint: disable=redefined-outer-name
) -> FixtureContext[dict[str, str]]:
    mock_environ = {
        **next(testkit.environ(fixtures), {}),
        "BUILD_PUBLISHER_API_KEY_ENABLE": "no",
        "BUILD_PUBLISHER_JENKINS_BASE_URL": "https://jenkins.invalid/",
        "BUILD_PUBLISHER_RECORDS_BACKEND": "memory",
        "BUILD_PUBLISHER_STORAGE_PATH": str(fixtures.tmpdir / "gbp"),
        "BUILD_PUBLISHER_WORKER_BACKEND": "sync",
        "BUILD_PUBLISHER_WORKER_THREAD_WAIT": "yes",
        **(environ or {}),
    }
    with mock.patch.dict(os.environ, mock_environ):
        yield mock_environ


@fixture()
def gbp(
    _fixtures: Fixtures, url: str = "http://test.invalid/", auth: AuthDict | None = None
) -> GBP:
    """Return a GBP instance with a mock session attribute"""
    # pylint: disable=protected-access
    _gbp = GBP(url, auth=auth)
    headers = _gbp.query._session.headers
    _gbp.query._session = mock.Mock()
    _gbp.query._session.headers = headers

    return _gbp


@fixture("tmpdir")
def user_config_dir(fixtures: Fixtures):
    with mock.patch(
        "gbpcli.platformdirs.user_config_dir", return_value=fixtures.tmpdir
    ) as patch:
        yield patch
