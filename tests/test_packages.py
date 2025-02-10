"""Tests for the packages subcommand"""

# pylint: disable=missing-function-docstring,protected-access
from unittest_fixtures import requires

from gbpcli.subcommands.packages import handler as packages

from . import TestCase, load_data, make_response, parse_args, print_command


@requires("gbp", "console")
class PackagesTestCase(TestCase):
    """packages() tests"""

    maxDiff = None

    def test(self):
        cmdline = "gbp packages babette 268"
        args = parse_args(cmdline)
        gbp = self.fixtures.gbp
        console = self.fixtures.console
        make_response(gbp, "packages.json")

        print_command(cmdline, console)
        status = packages(args, gbp, console)

        self.assertEqual(status, 0)
        expected = "$ gbp packages babette 268\n" + load_data("packages.txt").decode(
            "utf-8"
        )
        self.assertEqual(console.out.file.getvalue(), expected)
        self.assert_graphql(gbp, gbp.query.gbpcli.packages, id="babette.268")

    def test_when_build_does_not_exist_prints_error(self):
        cmdline = "gbp packages bogus 268"
        args = parse_args(cmdline)
        gbp = self.fixtures.gbp
        console = self.fixtures.console
        no_build = {"data": {"build": None}}
        make_response(gbp, no_build)

        status = packages(args, gbp, console)

        self.assertEqual(status, 1)
        self.assertEqual(console.err.file.getvalue(), "Not Found\n")
