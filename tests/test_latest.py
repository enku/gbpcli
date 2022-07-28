"""Tests for the latest subcommand"""
# pylint: disable=missing-function-docstring
from argparse import Namespace
from unittest import mock

from gbpcli import queries
from gbpcli.subcommands.latest import handler as latest

from . import LOCAL_TIMEZONE, TestCase, mock_print


@mock.patch("gbpcli.LOCAL_TIMEZONE", new=LOCAL_TIMEZONE)
@mock_print("gbpcli.subcommands.latest")
class LatestTestCase(TestCase):
    """latest() tests"""

    def test(self, _print_mock):
        args = Namespace(machine="lighthouse")
        self.make_response("latest.json")

        status = latest(args, self.gbp, self.console)

        self.assertEqual(status, 0)
        expected = "3113\n"
        self.assertEqual(self.console.getvalue(), expected)
        self.assert_graphql(queries.latest, machine="lighthouse")

    def test_should_print_error_when_not_found(self, print_mock):
        args = Namespace(machine="bogus")
        self.make_response({"data": {"latest": None}})

        status = latest(args, self.gbp, self.console)

        self.assertEqual(status, 1)
        self.assertEqual(
            print_mock.stderr.getvalue(), "No builds exist for the given machine\n"
        )
