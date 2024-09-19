"""Unittest fixtures"""

# pylint: disable=missing-docstring

import io
import os
import tempfile
from unittest import mock

import rich.console
from rich.theme import Theme
from unittest_fixtures import FixtureContext, FixtureOptions, Fixtures, depends

from gbpcli import GBP
from gbpcli.config import AuthDict
from gbpcli.theme import DEFAULT_THEME
from gbpcli.types import Console


def gbp(options: FixtureOptions, _fixtures: Fixtures) -> GBP:
    """Return a GBP instance with a mock session attribute"""
    # pylint: disable=protected-access
    gbp_options = options.get("gbp", {})
    url = gbp_options.get("url", "http://test.invalid/")
    auth: AuthDict | None = gbp_options.get("auth", None)
    _gbp = GBP(url, auth=auth)
    headers = _gbp.query._session.headers
    _gbp.query._session = mock.Mock()
    _gbp.query._session.headers = headers

    return _gbp


def console(_options: FixtureOptions, _fixtures: Fixtures) -> GBP:
    return mock.Mock(spec=Console, out=MockConsole(), err=MockConsole())


def tempdir(_options: FixtureOptions, _fixtures: Fixtures) -> FixtureContext[str]:
    """Create a tempdir for the given test

    The tempdir will be cleaned in the tearDown step
    """
    with tempfile.TemporaryDirectory() as _tempdir:
        yield _tempdir


def environ(options: FixtureOptions, _fixtures: Fixtures) -> FixtureContext[dict]:
    environ_options = options.get("environ", {})

    with mock.patch.dict(os.environ, environ_options, clear=True) as mocked_environ:
        yield mocked_environ


@depends(tempdir)
def user_config_dir(_options: FixtureOptions, fixtures: Fixtures):
    with mock.patch(
        "gbpcli.platformdirs.user_config_dir", return_value=fixtures.tempdir
    ) as patch:
        yield patch


class MockConsole:
    """Mock rich.console.Console

    Output is instead send to it's .stdout attribute, which is a StringIO.
    """

    def __init__(self):
        self.string_io = io.StringIO()
        self.console = rich.console.Console(
            file=self.string_io, theme=Theme(DEFAULT_THEME)
        )

    def print(self, *args, **kwargs):
        """Print to self.stdout"""
        return self.console.print(*args, **kwargs)

    def getvalue(self) -> str:
        """Return everying printed to the console"""
        return self.string_io.getvalue()
