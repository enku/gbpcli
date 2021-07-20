"""Tests for the latest subcommand"""
# pylint: disable=missing-function-docstring
import io
import sys
import unittest
from functools import partial
from json import loads as parse
from unittest import mock

from gbpcli.subcommands.latest import handler as latest

from . import LOCAL_TIMEZONE, load_data, make_response


@mock.patch("gbpcli.LOCAL_TIMEZONE", new=LOCAL_TIMEZONE)
@mock.patch("gbpcli.subcommands.latest.print")
class LatestTestCase(unittest.TestCase):
    """latest() tests"""

    def test(self, print_mock):
        stdout = io.StringIO()
        print_mock.side_effect = partial(print, file=stdout)
        args_mock = mock.Mock(
            url="http://test.invalid/", machine="lighthouse", number=2080
        )
        mock_json = parse(load_data("latest.json"))
        args_mock.session.get.return_value = make_response(json=mock_json)

        latest(args_mock)

        expected = "2085\n"
        self.assertEqual(stdout.getvalue(), expected)
        args_mock.session.get.assert_called_once_with(
            "http://test.invalid/api/builds/lighthouse/latest"
        )

    def test_should_print_error_when_returned(self, print_mock):
        args_mock = mock.Mock(
            url="http://test.invalid/", machine="lighthouse", number=2080
        )
        mock_json = {"error": "This is bad"}
        args_mock.session.get.return_value = make_response(json=mock_json)

        status = latest(args_mock)

        print_mock.assert_called_once_with("This is bad", file=sys.stderr)
        self.assertEqual(status, 1)
