"""Tests for the latest subcommand"""

# pylint: disable=missing-function-docstring,protected-access
from unittest import mock

from unittest_fixtures import requires

from gbpcli.subcommands.latest import handler as latest

from . import LOCAL_TIMEZONE, TestCase, make_response, parse_args, print_command


@requires("gbp", "console")
@mock.patch("gbpcli.render.LOCAL_TIMEZONE", new=LOCAL_TIMEZONE)
class LatestTestCase(TestCase):
    """latest() tests"""

    def test(self):
        cmdline = "gbp latest lighthouse"
        args = parse_args(cmdline)
        gbp = self.fixtures.gbp
        console = self.fixtures.console
        make_response(gbp, "latest.json")

        print_command(cmdline, console)
        status = latest(args, gbp, console)

        self.assertEqual(status, 0)
        expected = "$ gbp latest lighthouse\n3113\n"
        self.assertEqual(console.out.file.getvalue(), expected)
        self.assert_graphql(gbp, gbp.query.gbpcli.latest, machine="lighthouse")

    def test_should_print_error_when_not_found(self):
        cmdline = "gbp latest bogus"
        args = parse_args(cmdline)
        gbp = self.fixtures.gbp
        console = self.fixtures.console
        make_response(gbp, {"data": {"latest": None}})

        status = latest(args, gbp, console)

        self.assertEqual(status, 1)
        self.assertEqual(
            self.fixtures.console.err.file.getvalue(),
            "No builds exist for the given machine\n",
        )
