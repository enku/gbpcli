"""Tests for the show subcommand"""
# pylint: disable=missing-function-docstring
import unittest
from argparse import Namespace
from json import loads as parse
from unittest import mock

from gbpcli import queries
from gbpcli.subcommands.show import handler as show

from . import LOCAL_TIMEZONE, load_data, make_gbp, make_response, mock_print


@mock.patch("gbpcli.utils.LOCAL_TIMEZONE", new=LOCAL_TIMEZONE)
@mock_print("gbpcli.subcommands.show")
class ShowTestCase(unittest.TestCase):
    """show() tests"""

    maxDiff = None

    def test(self, print_mock):
        args = Namespace(machine="lighthouse", number=2080)
        mock_json = parse(load_data("show.json"))
        gbp = make_gbp()
        gbp.session.post.return_value = make_response(json=mock_json)

        show(args, gbp)

        expected = """\
Build: lighthouse/3109
Submitted: Sat Oct  2 07:26:19 2021 -0700
Completed: Sat Oct  2 07:41:25 2021 -0700
Published: yes
Keep: no

    Packages built:
    
    * app-text/poppler-21.10.0-1
    * dev-perl/URI-5.90.0-1
    * net-im/signal-desktop-bin-5.18.0-1
    * net-print/cups-filters-1.28.10-3
"""
        self.assertEqual(print_mock.stdout.getvalue(), expected)
        gbp.session.post.assert_called_once_with(
            gbp.url,
            json={
                "query": queries.build,
                "variables": {"name": "lighthouse", "number": 2080},
            },
            headers=gbp.headers,
        )

    def test_should_get_latest_when_number_is_none(self, _print_mock):
        args = Namespace(machine="lighthouse", number=None)
        mock_latest = make_response(json={"data": {"latest": {"number": 2080}}})
        mock_json = parse(load_data("show.json"))
        gbp = make_gbp()
        gbp.session.post.side_effect = (mock_latest, make_response(json=mock_json))

        status = show(args, gbp)

        expected_calls = [
            mock.call(
                gbp.url,
                json={"query": queries.latest, "variables": {"name": "lighthouse"}},
                headers=gbp.headers,
            ),
            mock.call(
                gbp.url,
                json={
                    "query": queries.build,
                    "variables": {"name": "lighthouse", "number": 2080},
                },
                headers=gbp.headers,
            ),
        ]
        gbp.session.post.assert_has_calls(expected_calls)
        self.assertEqual(status, 0)

    def test_should_print_error_when_build_does_not_exist(self, print_mock):
        args = Namespace(machine="bogus", number=934)
        gbp = make_gbp()
        gbp.session.post.return_value = make_response(json={"data": {"build": None}})

        status = show(args, gbp)

        self.assertEqual(status, 1)
        self.assertEqual(print_mock.stderr.getvalue(), "Build not found\n")
