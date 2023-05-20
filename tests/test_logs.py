"""Tests for the logs subcommand"""
# pylint: disable=missing-function-docstring
from argparse import Namespace
from unittest import mock

from gbpcli.subcommands.logs import handler as logs

from . import LOCAL_TIMEZONE, TestCase


@mock.patch("gbpcli.render.LOCAL_TIMEZONE", new=LOCAL_TIMEZONE)
class LogsTestCase(TestCase):
    """logs() tests"""

    def test(self):
        args = Namespace(machine="lighthouse", number="3113", search=False)
        self.make_response("logs.json")

        status = logs(args, self.gbp, self.console)

        self.assertEqual(status, 0)
        self.assertEqual(self.console.out.getvalue(), "This is a test!\n")
        self.assert_graphql(self.gbp.query.logs, id="lighthouse.3113")

    def test_should_print_error_when_logs_dont_exist(self):
        args = Namespace(machine="lighthouse", number="9999", search=False)
        self.make_response({"data": {"build": None}})

        status = logs(args, self.gbp, self.console)

        self.assertEqual(self.console.err.getvalue(), "Not Found\n")
        self.assertEqual(status, 1)

    def test_search_logs(self):
        args = Namespace(machine="lighthouse", number="this is a test", search=True)
        self.make_response("search_notes.json")
        self.make_response("logs.json")

        status = logs(args, self.gbp, self.console)

        self.assertEqual(status, 0)
        self.assert_graphql(
            self.gbp.query.search,
            machine="lighthouse",
            field="LOGS",
            key="this is a test",
        )
        expected = "lighthouse/10000\nThis is a test!\n"
        self.assertEqual(self.console.out.getvalue(), expected)
