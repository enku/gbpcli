"""Unittest tools"""

# pylint: disable=missing-docstring,redefined-outer-name,protected-access

import datetime as dt
from json import dumps as stringify
from json import loads as parse
from pathlib import Path
from typing import Any, Iterator
from unittest import TestCase as BaseTestCase
from unittest import mock

import gbp_testkit.fixtures as testkit
import requests
from rich.theme import Theme
from unittest_fixtures import FixtureContext, Fixtures, fixture

from gbpcli import GBP, graphql
from gbpcli.config import AuthDict

DATA_DIR = Path(__file__).resolve().parent / "data"
LOCAL_TIMEZONE = dt.timezone(dt.timedelta(days=-1, seconds=61200), "PDT")
NO_JSON = object()

__unittest = True  # pylint: disable=invalid-name


class TestCase(BaseTestCase):
    """Custom test case for gbpcli"""

    def assert_graphql(self, gbp, query: graphql.Query, index=0, **variables):
        """Assert that self.gbp made a the given graphql query"""
        calls = gbp.query._session.post.call_args_list

        try:
            call = calls[index]
        except IndexError:  # pragma: no cover
            self.fail("Query not called")

        assert call[0] == (gbp.query._url,)

        json = {"query": str(query), "variables": variables}
        expected = {"json": json}

        self.assertEqual(call[1], expected)


class ThemeTests(BaseTestCase):
    """Custom assertions for theme tests"""

    def assert_themes_are_equal(self, first: Theme, second: Theme, msg: Any = None):
        """Compare two rich themes"""
        self.assertEqual(first.styles, second.styles, msg)

    def assert_theme_color(self, theme: Theme, style: str, color: str, msg: Any = None):
        """Assert the theme's style is the given color"""
        style_color = theme.styles[style].color
        assert style_color is not None, msg
        self.assertEqual(style_color.name, color, msg)


@fixture()
def gbp(
    _fixtures: Fixtures, url: str = "http://test.invalid/", auth: AuthDict | None = None
) -> GBP:
    """Return a GBP instance with a mock session attribute"""
    _gbp = GBP(url, auth=auth)
    headers = _gbp.query._session.headers
    _gbp.query._session = mock.Mock()
    _gbp.query._session.headers = headers

    return _gbp


@fixture(testkit.tmpdir)
def user_config_dir(fixtures: Fixtures) -> FixtureContext[mock.Mock]:
    with mock.patch(
        "gbpcli.platformdirs.user_config_dir", return_value=fixtures.tmpdir
    ) as patch:
        yield patch


@fixture()
def local_timezone(
    _: Fixtures, local_timezone: dt.timezone = LOCAL_TIMEZONE
) -> FixtureContext[dt.timezone]:
    with mock.patch("gbpcli.render.LOCAL_TIMEZONE", new=local_timezone):
        yield local_timezone


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


def make_response(gbp, data):
    """Add 200 json response to mock post

    This is like http_response() below except it assumes all responses are 200
    responses and all content is JSON. Additionally it can be called more than once
    and adds responses for subsequent calls. If called with `None` as an argument,
    then any previously configured responses are cleared
    """
    # pylint: disable=protected-access
    match data:
        case None:
            gbp.query._session.post.side_effect = None
            return
        case str():
            mock_json = parse(load_data(data))
        case _:
            mock_json = data

    if not gbp.query._session.post.side_effect:
        gbp.query._session.post.side_effect = (http_response(json=mock_json),)
    else:
        gbp.query._session.post.side_effect = (
            *gbp.query._session.post.side_effect,
            http_response(json=mock_json),
        )


def load_data(filename: str) -> bytes:
    """Read and return content from filename in the data directory"""
    return (DATA_DIR / filename).read_bytes()


def load_ndjson(filename: str, start: int = 1) -> Iterator[Any]:
    """Iterate over a newline-delimited JSON file"""
    with open(DATA_DIR / filename, "r", encoding="UTF-8") as ndjson_file:
        for line_no, line in enumerate(ndjson_file, start=1):
            if line_no < start:
                continue

            yield parse(line)
