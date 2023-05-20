"""Tests for the packages subcommand"""
# pylint: disable=missing-function-docstring,protected-access
from argparse import Namespace

from gbpcli.subcommands.packages import handler as packages

from . import TestCase, load_data


class PackagesTestCase(TestCase):
    """packages() tests"""

    maxDiff = None

    def test(self):
        args = Namespace(machine="babette", number="268")
        self.make_response("packages.json")

        status = packages(args, self.gbp, self.console)

        self.assertEqual(status, 0)
        expected = load_data("packages.txt").decode("utf-8")
        self.assertEqual(self.console.out.getvalue(), expected)
        self.assert_graphql(self.gbp.query.packages, id="babette.268")

    def test_when_build_does_not_exist_prints_error(self):
        args = Namespace(machine="bogus", number="268")
        no_build = {"data": {"build": {"packages": None}}}
        self.make_response(no_build)

        status = packages(args, self.gbp, self.console)

        self.assertEqual(status, 1)
        self.assertEqual(self.console.err.getvalue(), "Not Found\n")
