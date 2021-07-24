"""Tests for the logs subcommand"""
# pylint: disable=missing-function-docstring
import unittest
from argparse import Namespace
from unittest import mock

from gbpcli.subcommands.logs import handler as logs

from . import LOCAL_TIMEZONE, make_gbp, make_response, mock_print


@mock.patch("gbpcli.LOCAL_TIMEZONE", new=LOCAL_TIMEZONE)
@mock_print("gbpcli.subcommands.logs")
class LogsTestCase(unittest.TestCase):
    """logs() tests"""

    def test(self, print_mock):
        args = Namespace(machine="lighthouse", number=2086)
        gbp = make_gbp()
        gbp.session.get.return_value = make_response()

        status = logs(args, gbp)

        self.assertEqual(status, 0)
        self.assertEqual(print_mock.stdout.getvalue(), "test\n")
        gbp.session.get.assert_called_once_with(
            "http://test.invalid/api/builds/lighthouse/2086/log"
        )

    def test_should_print_error_when_logs_dont_exist(self, print_mock):
        args = Namespace(machine="lighthouse", number=2086)
        gbp = make_gbp()
        gbp.session.get.return_value = make_response(status_code=404)

        status = logs(args, gbp)

        self.assertEqual(print_mock.stderr.getvalue(), "Not Found\n")
        self.assertEqual(status, 1)
