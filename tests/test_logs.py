"""Tests for the logs subcommand"""
# pylint: disable=missing-function-docstring
from argparse import Namespace
from unittest import mock

from gbpcli import queries
from gbpcli.subcommands.logs import handler as logs

from . import LOCAL_TIMEZONE, TestCase, mock_print


@mock.patch("gbpcli.LOCAL_TIMEZONE", new=LOCAL_TIMEZONE)
@mock_print("gbpcli.subcommands.logs")
class LogsTestCase(TestCase):
    """logs() tests"""

    def test(self, _print_mock):
        args = Namespace(machine="lighthouse", number="3113")
        self.make_response("logs.json")

        status = logs(args, self.gbp, self.console)

        self.assertEqual(status, 0)
        self.assertEqual(self.console.getvalue(), "This is a test!\n")
        self.assert_graphql(queries.logs, id="lighthouse.3113")

    def test_should_print_error_when_logs_dont_exist(self, print_mock):
        args = Namespace(machine="lighthouse", number="9999")
        self.make_response({"data": {"build": None}})

        status = logs(args, self.gbp, self.console)

        self.assertEqual(print_mock.stderr.getvalue(), "Not Found\n")
        self.assertEqual(status, 1)
