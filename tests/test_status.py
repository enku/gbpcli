"""Tests for the status subcommand"""

# pylint: disable=missing-function-docstring,protected-access
from unittest import mock

from gbp_testkit.helpers import parse_args, print_command
from unittest_fixtures import Fixtures, given

from gbpcli.subcommands.status import handler as status

from . import LOCAL_TIMEZONE, TestCase, make_response


@given("gbp", "console")
@mock.patch("gbpcli.render.LOCAL_TIMEZONE", new=LOCAL_TIMEZONE)
class StatusTestCase(TestCase):
    """status() tests"""

    def test(self, fixtures: Fixtures):
        cmdline = "gbp status lighthouse 3587"
        args = parse_args(cmdline)
        gbp = fixtures.gbp
        console = fixtures.console
        make_response(gbp, "status.json")

        print_command(cmdline, console)
        status(args, gbp, console)

        expected = """$ gbp status lighthouse 3587
╭────────────────────────────────────────────────╮
│ Build:          lighthouse 3587                │
│ BuildDate:      Fri Nov 12 21:23:34 2021 -0700 │
│ Submitted:      Fri Nov 12 21:25:53 2021 -0700 │
│ Completed:      Fri Nov 12 21:29:34 2021 -0700 │
│ Published:      no                             │
│ Keep:           no                             │
│ Tags:           @testing                       │
│ Packages-built: app-editors/vim-8.2.3582       │
│                 app-editors/vim-core-8.2.3582  │
╰────────────────────────────────────────────────╯

╭─────────────────────╮
│📎 Notes             │
├─────────────────────┤
│This is a build note.│
│Hello world!         │
╰─────────────────────╯
"""
        self.assertEqual(console.out.file.getvalue(), expected)
        self.assert_graphql(gbp, gbp.query.gbpcli.build, id="lighthouse.3587")

    def test_should_get_latest_when_number_is_none(self, fixtures: Fixtures):
        cmdline = "gbp status lighthouse"
        args = parse_args(cmdline)
        gbp = fixtures.gbp
        console = fixtures.console
        make_response(gbp, {"data": {"latest": {"id": "lighthouse.3587"}}})
        make_response(gbp, "status.json")

        print_command(cmdline, console)
        return_status = status(args, gbp, console)

        self.assert_graphql(gbp, gbp.query.gbpcli.latest, index=0, machine="lighthouse")
        self.assert_graphql(gbp, gbp.query.gbpcli.build, index=1, id="lighthouse.3587")
        self.assertEqual(return_status, 0)

    def test_should_print_error_when_build_does_not_exist(self, fixtures: Fixtures):
        cmdline = "gbp status bogus 934"
        args = parse_args(cmdline)
        gbp = fixtures.gbp
        console = fixtures.console
        make_response(gbp, {"data": {"build": None}})

        return_status = status(args, gbp, console)

        self.assertEqual(return_status, 1)
        self.assertEqual(console.err.file.getvalue(), "Not found\n")
