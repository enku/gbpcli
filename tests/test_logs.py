"""Tests for the logs subcommand"""

# pylint: disable=missing-function-docstring
from unittest import mock

from unittest_fixtures import requires

from gbpcli.subcommands.logs import handler as logs

from . import LOCAL_TIMEZONE, TestCase, make_response, parse_args, print_command


@requires("gbp", "console")
@mock.patch("gbpcli.render.LOCAL_TIMEZONE", new=LOCAL_TIMEZONE)
class LogsTestCase(TestCase):
    """logs() tests"""

    def test(self):
        cmdline = "gbp logs lighthouse 3113"
        args = parse_args(cmdline)
        gbp = self.fixtures.gbp
        console = self.fixtures.console
        make_response(gbp, "logs.json")

        print_command(cmdline, console)
        status = logs(args, gbp, console)

        self.assertEqual(status, 0)
        self.assertEqual(
            console.out.file.getvalue(), "$ gbp logs lighthouse 3113\nThis is a test!\n"
        )
        self.assert_graphql(gbp, gbp.query.gbpcli.logs, id="lighthouse.3113")

    def test_should_print_error_when_logs_dont_exist(self):
        cmdline = "gbp logs lighthouse 9999"
        args = parse_args(cmdline)
        gbp = self.fixtures.gbp
        console = self.fixtures.console
        make_response(gbp, {"data": {"build": None}})

        status = logs(args, gbp, console)

        self.assertEqual(console.err.file.getvalue(), "Not Found\n")
        self.assertEqual(status, 1)

    def test_search_logs(self):
        cmdline = "gbp logs -s lighthouse 'this is a test'"
        args = parse_args(cmdline)
        gbp = self.fixtures.gbp
        console = self.fixtures.console
        make_response(gbp, "search_notes.json")
        make_response(gbp, "logs.json")

        status = logs(args, gbp, console)

        self.assertEqual(status, 0)
        self.assert_graphql(
            gbp,
            gbp.query.gbpcli.search,
            machine="lighthouse",
            field="LOGS",
            key="this is a test",
        )
        expected = "lighthouse/10000\nThis is a test!\n"
        self.assertEqual(console.out.file.getvalue(), expected)
