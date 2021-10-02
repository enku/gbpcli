"""Tests for the logs subcommand"""
# pylint: disable=missing-function-docstring
import unittest
from argparse import Namespace
from json import loads as parse
from unittest import mock

from gbpcli import queries
from gbpcli.subcommands.logs import handler as logs

from . import LOCAL_TIMEZONE, load_data, make_gbp, make_response, mock_print


@mock.patch("gbpcli.LOCAL_TIMEZONE", new=LOCAL_TIMEZONE)
@mock_print("gbpcli.subcommands.logs")
class LogsTestCase(unittest.TestCase):
    """logs() tests"""

    def test(self, print_mock):
        args = Namespace(machine="lighthouse", number=3113)
        gbp = make_gbp()
        gbp.session.post.return_value = make_response(
            json=parse(load_data("logs.json"))
        )

        status = logs(args, gbp)

        self.assertEqual(status, 0)
        self.assertEqual(print_mock.stdout.getvalue(), "This is a test!\n")
        gbp.session.post.assert_called_once_with(
            gbp.url,
            json={
                "query": queries.logs,
                "variables": {"name": "lighthouse", "number": 3113},
            },
            headers=gbp.headers,
        )

    def test_should_print_error_when_logs_dont_exist(self, print_mock):
        args = Namespace(machine="lighthouse", number=9999)
        gbp = make_gbp()
        gbp.session.post.return_value = make_response(json={"data": {"build": None}})

        status = logs(args, gbp)

        self.assertEqual(print_mock.stderr.getvalue(), "Not Found\n")
        self.assertEqual(status, 1)
