"""Tests for the latest subcommand"""

# pylint: disable=missing-function-docstring,protected-access
from unittest import mock

from gbp_testkit.helpers import parse_args, print_command
from unittest_fixtures import Fixtures, given

from gbpcli.subcommands.latest import handler as latest

from . import LOCAL_TIMEZONE, TestCase, make_response


@given("gbp", "console")
@mock.patch("gbpcli.render.LOCAL_TIMEZONE", new=LOCAL_TIMEZONE)
class LatestTestCase(TestCase):
    """latest() tests"""

    def test(self, fixtures: Fixtures):
        cmdline = "gbp latest lighthouse"
        args = parse_args(cmdline)
        gbp = fixtures.gbp
        console = fixtures.console
        make_response(gbp, "latest.json")

        print_command(cmdline, console)
        status = latest(args, gbp, console)

        self.assertEqual(status, 0)
        expected = "$ gbp latest lighthouse\n3113\n"
        self.assertEqual(console.out.file.getvalue(), expected)
        self.assert_graphql(gbp, gbp.query.gbpcli.latest, machine="lighthouse")

    def test_should_print_error_when_not_found(self, fixtures: Fixtures):
        cmdline = "gbp latest bogus"
        args = parse_args(cmdline)
        gbp = fixtures.gbp
        console = fixtures.console
        make_response(gbp, {"data": {"latest": None}})

        status = latest(args, gbp, console)

        self.assertEqual(status, 1)
        self.assertEqual(
            fixtures.console.err.file.getvalue(),
            "No builds exist for the given machine\n",
        )
