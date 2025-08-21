"""Tests for the status subcommand"""

# pylint: disable=missing-function-docstring,protected-access
import datetime as dt

import gbp_testkit.fixtures as testkit
from gbp_testkit.helpers import parse_args, print_command
from gentoo_build_publisher import publisher
from gentoo_build_publisher.types import Build
from unittest_fixtures import Fixtures, fixture, given

from gbpcli.subcommands.status import handler as status

from . import lib

BUILD = Build(machine="lighthouse", build_id="3587")


@fixture(testkit.publisher)
def pulled_build(_: Fixtures) -> None:
    build = BUILD
    builder = publisher.jenkins.artifact_builder  # type: ignore
    builder.build(build, "app-editors/vim-8.2.3582")
    builder.build(build, "app-editors/vim-core-8.2.3582")
    publisher.pull(build, tags=["testing"])

    publisher.save(
        publisher.record(build),
        built=dt.datetime(2021, 11, 13, 4, 23, 34, tzinfo=dt.UTC),
        submitted=dt.datetime(2021, 11, 13, 4, 25, 53, tzinfo=dt.UTC),
        completed=dt.datetime(2021, 11, 13, 4, 29, 34, tzinfo=dt.UTC),
        note="This is a build note.\nHello world!",
    )


@given(testkit.gbp, testkit.console, lib.local_timezone, pulled_build)
class StatusTestCase(lib.TestCase):
    """status() tests"""

    def test(self, fixtures: Fixtures):
        cmdline = "gbp status lighthouse 3587"
        args = parse_args(cmdline)
        console = fixtures.console

        print_command(cmdline, console)
        status(args, fixtures.gbp, console)

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

    def test_should_get_latest_when_number_is_none(self, fixtures: Fixtures):
        cmdline = "gbp status lighthouse"
        args = parse_args(cmdline)
        console = fixtures.console

        print_command(cmdline, console)
        return_status = status(args, fixtures.gbp, console)

        self.assertEqual(return_status, 0)
        self.assertTrue(" lighthouse 3587 " in console.out.file.getvalue())

    def test_should_print_error_when_build_does_not_exist(self, fixtures: Fixtures):
        cmdline = "gbp status bogus 934"
        args = parse_args(cmdline)
        console = fixtures.console

        return_status = status(args, fixtures.gbp, console)

        self.assertEqual(return_status, 1)
        self.assertEqual(console.err.file.getvalue(), "Not found\n")
