"""Tests for the Gentoo Build Publisher CLI"""
# pylint: disable=protected-access
import datetime
import io
import sys
import unittest
from functools import partial
from json import dumps as stringify
from json import loads as parse
from pathlib import Path
from typing import Any, Iterator
from unittest import mock

import requests
import rich.console
from rich.theme import Theme

from gbpcli import GBP, Console, graphql
from gbpcli.theme import DEFAULT_THEME

DATA_DIR = Path(__file__).resolve().parent / "data"
LOCAL_TIMEZONE = datetime.timezone(datetime.timedelta(days=-1, seconds=61200), "PDT")
NO_JSON = object()


class TestCase(unittest.TestCase):
    """Custom test case for gbpcli"""

    def setUp(self):
        super().setUp()

        self.gbp = make_gbp()
        self.console = mock.Mock(spec=Console, out=MockConsole(), err=MockConsole())

    def make_response(self, data):
        """Add 200 json response to mock post

        This is like make_response() below except it assumes all responses are 200
        responses and all content is JSON. Additionally it can be called more than once
        and adds responses for subsequent calls. If called with `None` as an argument,
        then any previously configured responses are cleared
        """
        if data is None:
            self.gbp.query._session.post.side_effect = None
            return

        if isinstance(data, str):
            mock_json = parse(load_data(data))
        else:
            mock_json = data

        if not self.gbp.query._session.post.side_effect:
            self.gbp.query._session.post.side_effect = (make_response(json=mock_json),)
        else:
            self.gbp.query._session.post.side_effect = (
                *self.gbp.query._session.post.side_effect,
                make_response(json=mock_json),
            )

    def assert_graphql(self, query: graphql.Query, index=0, **variables):
        """Assert that self.gbp made a the given graphql query"""
        calls = self.gbp.query._session.post.call_args_list

        try:
            call = calls[index]
        except IndexError:
            self.fail("Query not called")

        assert call[0] == (self.gbp.query._url,)

        json = {"query": str(query), "variables": variables}
        expected = {"json": json, "headers": graphql.Query.headers}

        self.assertEqual(call[1], expected)


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


def make_response(status_code=200, json=NO_JSON, content=None) -> requests.Response:
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


def make_gbp(url: str = "http://test.invalid/") -> GBP:
    """Return a GBP instance with a mock session attribute"""
    gbp = GBP(url)
    gbp.query._session = mock.Mock()

    return gbp


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
