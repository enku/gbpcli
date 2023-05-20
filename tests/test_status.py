"""Tests for the status subcommand"""
# pylint: disable=missing-function-docstring,protected-access
from argparse import Namespace
from unittest import mock

from gbpcli.subcommands.status import handler as status

from . import LOCAL_TIMEZONE, TestCase


@mock.patch("gbpcli.render.LOCAL_TIMEZONE", new=LOCAL_TIMEZONE)
class StatusTestCase(TestCase):
    """status() tests"""

    maxDiff = None

    def test(self):
        args = Namespace(machine="lighthouse", number="3587")
        self.make_response("status.json")

        status(args, self.gbp, self.console)

        expected = """\
╭────────────────────────────────────────────────╮
│ Build:          lighthouse 3587                │
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
        self.assertEqual(self.console.out.getvalue(), expected)
        self.assert_graphql(self.gbp.query.build, id="lighthouse.3587")

    def test_should_get_latest_when_number_is_none(self):
        args = Namespace(machine="lighthouse", number=None)
        self.make_response({"data": {"latest": {"id": "lighthouse.3587"}}})
        self.make_response("status.json")

        return_status = status(args, self.gbp, self.console)

        self.assert_graphql(self.gbp.query.latest, index=0, machine="lighthouse")
        self.assert_graphql(self.gbp.query.build, index=1, id="lighthouse.3587")
        self.assertEqual(return_status, 0)

    def test_should_print_error_when_build_does_not_exist(self):
        args = Namespace(machine="bogus", number="934")
        self.make_response({"data": {"build": None}})

        return_status = status(args, self.gbp, self.console)

        self.assertEqual(return_status, 1)
        self.assertEqual(self.console.err.getvalue(), "Not found\n")
