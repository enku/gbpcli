"""Tests for the Gentoo Build Publisher CLI"""

# pylint: disable=protected-access
import argparse
import datetime
import shlex
import tempfile
from json import dumps as stringify
from json import loads as parse
from pathlib import Path
from typing import Any, Iterator
from unittest import TestCase as BaseTestCase

import requests
from rich.theme import Theme

import gbpcli
from gbpcli import graphql
from gbpcli.config import Config
from gbpcli.types import Console

DATA_DIR = Path(__file__).resolve().parent / "data"
LOCAL_TIMEZONE = datetime.timezone(datetime.timedelta(days=-1, seconds=61200), "PDT")
NO_JSON = object()

__unittest = True  # pylint: disable=invalid-name


class TestCase(BaseTestCase):
    """Custom test case for gbpcli"""

    def assert_graphql(self, gbp, query: graphql.Query, index=0, **variables):
        """Assert that self.gbp made a the given graphql query"""
        calls = gbp.query._session.post.call_args_list

        try:
            call = calls[index]
        except IndexError:
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


def make_response(gbp, data):
    """Add 200 json response to mock post

    This is like http_response() below except it assumes all responses are 200
    responses and all content is JSON. Additionally it can be called more than once
    and adds responses for subsequent calls. If called with `None` as an argument,
    then any previously configured responses are cleared
    """
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


def parse_args(cmdline: str) -> argparse.Namespace:
    """Return cmdline as parsed arguments"""
    args = shlex.split(cmdline)
    parser = gbpcli.build_parser(Config(url="http://gbp.invalid/"))

    return parser.parse_args(args[1:])


def print_command(cmdline: str, console: Console) -> None:
    """Pretty print the cmdline to console"""
    console.out.print(f"[green]$ [/green]{cmdline}")
