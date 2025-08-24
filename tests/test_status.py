"""Tests for the status subcommand"""

# pylint: disable=missing-docstring
from unittest import TestCase

import gbp_testkit.fixtures as testkit
from gbp_testkit.helpers import LOCAL_TIMEZONE
from gentoo_build_publisher.types import Build
from unittest_fixtures import Fixtures, given, where

from . import lib

BUILD = Build(machine="lighthouse", build_id="3587")
PACKAGES = ["app-editors/vim-8.2.3582", "app-editors/vim-core-8.2.3582"]


@given(testkit.gbpcli, lib.pulled_build, local_timezone=testkit.patch)
@where(pulled_build__build=BUILD, pulled_build__packages=PACKAGES)
@where(pulled_build__tags=["testing"])
@where(pulled_build__note="This is a build note.\nHello world!\n")
@where(local_timezone__target="gbpcli.render.LOCAL_TIMEZONE")
@where(local_timezone__new=LOCAL_TIMEZONE)
class StatusTestCase(TestCase):
    """status() tests"""

    def test(self, fixtures: Fixtures):
        fixtures.gbpcli("gbp status lighthouse 3587")

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
        self.assertEqual(fixtures.console.stdout, expected)

    def test_should_get_latest_when_number_is_none(self, fixtures: Fixtures):
        return_status = fixtures.gbpcli("gbp status lighthouse")

        self.assertEqual(return_status, 0)
        self.assertTrue(" lighthouse 3587 " in fixtures.console.stdout)

    def test_should_print_error_when_build_does_not_exist(self, fixtures: Fixtures):
        return_status = fixtures.gbpcli("gbp status bogus 934")

        self.assertEqual(return_status, 1)
        self.assertEqual(fixtures.console.stderr, "Not found\n")
