"""Tests for the packages subcommand"""

# pylint: disable=missing-function-docstring,protected-access
import gbp_testkit.fixtures as testkit
from gbp_testkit.helpers import parse_args, print_command
from unittest_fixtures import Fixtures, given

from gbpcli.subcommands.packages import handler as packages

from . import lib


@given(lib.gbp, testkit.console)
class PackagesTestCase(lib.TestCase):
    """packages() tests"""

    def test(self, fixtures: Fixtures):
        cmdline = "gbp packages babette 268"
        args = parse_args(cmdline)
        gbp = fixtures.gbp
        console = fixtures.console
        lib.make_response(gbp, "packages.json")

        print_command(cmdline, console)
        status = packages(args, gbp, console)

        self.assertEqual(status, 0)
        expected = "$ gbp packages babette 268\n" + lib.load_data(
            "packages.txt"
        ).decode("utf-8")
        self.assertEqual(console.out.file.getvalue(), expected)
        self.assert_graphql(
            gbp, gbp.query.gbpcli.packages, id="babette.268", buildId=False
        )

    def test_with_build_ids(self, fixtures: Fixtures):
        cmdline = "gbp packages -b lighthouse 33655"
        args = parse_args(cmdline)
        gbp = fixtures.gbp
        console = fixtures.console
        lib.make_response(gbp, "packages-b.json")

        print_command(cmdline, console)
        status = packages(args, gbp, console)

        self.assertEqual(status, 0)
        expected = "$ gbp packages -b lighthouse 33655\n" + lib.load_data(
            "packages-b.txt"
        ).decode("utf-8")
        self.assertEqual(console.out.file.getvalue(), expected)
        self.assert_graphql(
            gbp, gbp.query.gbpcli.packages, id="lighthouse.33655", buildId=True
        )

    def test_when_build_does_not_exist_prints_error(self, fixtures: Fixtures):
        cmdline = "gbp packages bogus 268"
        args = parse_args(cmdline)
        gbp = fixtures.gbp
        console = fixtures.console
        no_build = {"data": {"build": None}}
        lib.make_response(gbp, no_build)

        status = packages(args, gbp, console)

        self.assertEqual(status, 1)
        self.assertEqual(console.err.file.getvalue(), "Not Found\n")
