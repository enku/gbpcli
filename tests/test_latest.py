"""Tests for the latest subcommand"""
# pylint: disable=missing-function-docstring
import unittest
from argparse import Namespace
from json import loads as parse
from unittest import mock

from gbpcli import queries
from gbpcli.subcommands.latest import handler as latest

from . import LOCAL_TIMEZONE, load_data, make_gbp, make_response, mock_print


@mock.patch("gbpcli.LOCAL_TIMEZONE", new=LOCAL_TIMEZONE)
@mock_print("gbpcli.subcommands.latest")
class LatestTestCase(unittest.TestCase):
    """latest() tests"""

    def test(self, print_mock):
        args = Namespace(machine="lighthouse")
        mock_json = parse(load_data("latest.json"))
        gbp = make_gbp()
        gbp.session.post.return_value = make_response(json=mock_json)

        status = latest(args, gbp)

        self.assertEqual(status, 0)
        expected = "3113\n"
        self.assertEqual(print_mock.stdout.getvalue(), expected)
        gbp.session.post.assert_called_once_with(
            gbp.url,
            json={"query": queries.latest, "variables": {"name": "lighthouse"}},
            headers=gbp.headers,
        )

    def test_should_print_error_when_not_found(self, print_mock):
        args = Namespace(machine="bogus")
        gbp = make_gbp()
        gbp.session.post.return_value = make_response(json={"data": {"latest": None}})

        status = latest(args, gbp)

        self.assertEqual(status, 1)
        self.assertEqual(
            print_mock.stderr.getvalue(), "No builds exist for the given machine\n"
        )
