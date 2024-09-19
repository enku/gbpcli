"""Tests for the packages subcommand"""

# pylint: disable=missing-function-docstring,protected-access
from argparse import Namespace

from unittest_fixtures import requires

from gbpcli.subcommands.packages import handler as packages

from . import TestCase, load_data, make_response


@requires("gbp", "console")
class PackagesTestCase(TestCase):
    """packages() tests"""

    maxDiff = None

    def test(self):
        args = Namespace(machine="babette", number="268")
        gbp = self.fixtures.gbp
        make_response(gbp, "packages.json")

        status = packages(args, gbp, self.fixtures.console)

        self.assertEqual(status, 0)
        expected = load_data("packages.txt").decode("utf-8")
        self.assertEqual(self.fixtures.console.out.getvalue(), expected)
        self.assert_graphql(gbp, gbp.query.gbpcli.packages, id="babette.268")

    def test_when_build_does_not_exist_prints_error(self):
        args = Namespace(machine="bogus", number="268")
        gbp = self.fixtures.gbp
        no_build = {"data": {"build": None}}
        make_response(gbp, no_build)

        status = packages(args, gbp, self.fixtures.console)

        self.assertEqual(status, 1)
        self.assertEqual(self.fixtures.console.err.getvalue(), "Not Found\n")
