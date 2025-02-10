"""Unittest fixtures"""

# pylint: disable=missing-docstring

import io
import os
import tempfile
from unittest import mock

import rich.console
from unittest_fixtures import FixtureContext, FixtureOptions, Fixtures, depends

from gbpcli import GBP
from gbpcli.config import AuthDict
from gbpcli.theme import get_theme_from_string
from gbpcli.types import Console

COUNTER = 0


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


@depends()
def console(_options: FixtureOptions, _fixtures: Fixtures) -> FixtureContext[Console]:
    outfile = io.StringIO()
    errfile = io.StringIO()
    theme = get_theme_from_string(os.getenv("GBPCLI_COLORS", ""))
    out = rich.console.Console(
        file=outfile, width=88, theme=theme, highlight=False, record=True
    )
    err = rich.console.Console(file=errfile, width=88, record=True)
    c = Console(out=out, err=err)

    yield c

    # pylint: disable=no-member,global-statement
    if "SAVE_VIRTUAL_CONSOLE" in os.environ and c.out.file.getvalue():  # type: ignore
        global COUNTER

        COUNTER += 1
        filename = f"{COUNTER}.svg"
        c.out.save_svg(filename, title="Gentoo Build Publisher")


def tempdir(_options: FixtureOptions, _fixtures: Fixtures) -> FixtureContext[str]:
    """Create a tempdir for the given test

    The tempdir will be cleaned in the tearDown step
    """
    with tempfile.TemporaryDirectory() as _tempdir:
        yield _tempdir


def environ(options: FixtureOptions, _fixtures: Fixtures) -> FixtureContext[dict]:
    environ_options = options.get("environ", {})

    with mock.patch.dict(os.environ, environ_options) as mocked_environ:
        yield mocked_environ


@depends(tempdir)
def user_config_dir(_options: FixtureOptions, fixtures: Fixtures):
    with mock.patch(
        "gbpcli.platformdirs.user_config_dir", return_value=fixtures.tempdir
    ) as patch:
        yield patch
