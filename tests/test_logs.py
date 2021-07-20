"""Tests for the logs subcommand"""
# pylint: disable=missing-function-docstring
import io
import sys
import unittest
from functools import partial
from unittest import mock

from gbpcli.subcommands.logs import handler as logs

from . import LOCAL_TIMEZONE, make_response


@mock.patch("gbpcli.LOCAL_TIMEZONE", new=LOCAL_TIMEZONE)
@mock.patch("gbpcli.subcommands.logs.print")
class LogsTestCase(unittest.TestCase):
    """logs() tests"""

    def test(self, print_mock):
        stdout = io.StringIO()
        print_mock.side_effect = partial(print, file=stdout)
        args_mock = mock.Mock(
            url="http://test.invalid/", machine="lighthouse", number=2086
        )
        args_mock.session.get.return_value = make_response()

        logs(args_mock)

        self.assertEqual(stdout.getvalue(), "test\n")
        args_mock.session.get.assert_called_once_with(
            "http://test.invalid/api/builds/lighthouse/2086/log"
        )

    def test_should_print_error_and_exit_when_logs_dont_exist(self, print_mock):
        args_mock = mock.Mock(
            url="http://test.invalid/", machine="lighthouse", number=2086
        )
        args_mock.session.get.return_value = make_response(status_code=404)

        status = logs(args_mock)

        print_mock.assert_called_once_with("Not Found", file=sys.stderr)
        self.assertEqual(status, 1)
