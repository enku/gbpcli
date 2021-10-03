"""Tests for the packages subcommand"""
# pylint: disable=missing-function-docstring
import unittest
from argparse import Namespace
from json import loads as parse

from gbpcli import queries
from gbpcli.subcommands.packages import handler as packages

from . import load_data, make_gbp, make_response, mock_print


@mock_print("gbpcli.subcommands.packages")
class PackagesTestCase(unittest.TestCase):
    """packages() tests"""

    maxDiff = None

    def test(self, print_mock):
        args = Namespace(machine="babette", number=268)
        mock_json = parse(load_data("packages.json"))
        gbp = make_gbp()
        gbp.session.post.return_value = make_response(json=mock_json)

        status = packages(args, gbp)

        self.assertEqual(status, 0)
        expected = load_data("packages.txt").decode("utf-8")
        self.assertEqual(print_mock.stdout.getvalue(), expected)
        gbp.session.post.assert_called_once_with(
            gbp.url,
            json={
                "query": queries.packages,
                "variables": {"name": "babette", "number": 268},
            },
            headers=gbp.headers,
        )

    def test_when_build_does_not_exist_prints_error(self, print_mock):
        args = Namespace(machine="bogus", number=268)
        gbp = make_gbp()
        no_build = {"data": {"packages": None}}
        gbp.session.post.return_value = make_response(json=no_build)

        status = packages(args, gbp)

        self.assertEqual(status, 1)
        self.assertEqual(print_mock.stderr.getvalue(), "Not Found\n")
