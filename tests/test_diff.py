"""Tests for the diff subcommand"""

# pylint: disable=missing-function-docstring,protected-access
import datetime as dt
from unittest import TestCase

import gbp_testkit.fixtures as testkit
from gbp_testkit.helpers import LOCAL_TIMEZONE
from gentoo_build_publisher import publisher
from gentoo_build_publisher.types import Build
from unittest_fixtures import Fixtures, given, where

from . import lib


@given(testkit.gbpcli, testkit.console, local_timezone=testkit.patch)
@where(local_timezone__target="gbpcli.render.LOCAL_TIMEZONE")
@where(local_timezone__new=LOCAL_TIMEZONE)
@given(build2=lib.pulled_build)
@where(build2__build=Build(machine="lighthouse", build_id="3112"))
@where(
    build2__packages=[
        "app-accessibility/at-spi2-atk-2.46.0",
        "app-accessibility/at-spi2-core-2.46.0",
        "dev-libs/atk-2.46.0",
        "dev-libs/libgusb-0.4.1",
        "sys-kernel/vanilla-sources-6.0.0",
    ]
)
@where(build2__built=dt.datetime(2022, 10, 3, 11, 38, 28, tzinfo=dt.UTC))
@where(build2__clear=True)
@given(build1=lib.pulled_build)
@where(build1__build=Build(machine="lighthouse", build_id="3111"))
@where(
    build1__packages=[
        "app-accessibility/at-spi2-atk-2.38.0",
        "app-accessibility/at-spi2-core-2.44.1",
        "dev-libs/atk-2.38.0",
        "dev-libs/libgusb-0.4.0",
        "sys-kernel/vanilla-sources-5.19.12",
    ]
)
@where(build1__built=dt.datetime(2022, 10, 2, 19, 10, 2, tzinfo=dt.UTC))
class DiffTestCase(TestCase):
    """diff() tests"""

    def test_should_display_diffs(self, fixtures: Fixtures):
        status = fixtures.gbpcli("gbp diff lighthouse 3111 3112")

        self.assertEqual(status, 0)
        expected = """$ gbp diff lighthouse 3111 3112
diff -r lighthouse/3111 lighthouse/3112
--- lighthouse/3111 Sun Oct  2 12:10:02 2022 -0700
+++ lighthouse/3112 Mon Oct  3 04:38:28 2022 -0700
-app-accessibility/at-spi2-atk-2.38.0-1
+app-accessibility/at-spi2-atk-2.46.0-1
-app-accessibility/at-spi2-core-2.44.1-1
+app-accessibility/at-spi2-core-2.46.0-1
-dev-libs/atk-2.38.0-1
+dev-libs/atk-2.46.0-1
-dev-libs/libgusb-0.4.0-1
+dev-libs/libgusb-0.4.1-1
-sys-kernel/vanilla-sources-5.19.12-1
+sys-kernel/vanilla-sources-6.0.0-1
"""
        self.assertEqual(fixtures.console.stdout, expected)

    def test_should_print_nothing_when_no_diffs(self, fixtures: Fixtures):
        cmdline = "gbp diff lighthouse 3111 3111"

        fixtures.gbpcli(cmdline)

        self.assertEqual(fixtures.console.stdout, f"$ {cmdline}\n")

    def test_when_right_is_none_should_use_latest(self, fixtures: Fixtures):
        status = fixtures.gbpcli("gbp diff lighthouse 3111")

        self.assertEqual(status, 0)
        expected = """$ gbp diff lighthouse 3111
diff -r lighthouse/3111 lighthouse/3112
--- lighthouse/3111 Sun Oct  2 12:10:02 2022 -0700
+++ lighthouse/3112 Mon Oct  3 04:38:28 2022 -0700
-app-accessibility/at-spi2-atk-2.38.0-1
+app-accessibility/at-spi2-atk-2.46.0-1
-app-accessibility/at-spi2-core-2.44.1-1
+app-accessibility/at-spi2-core-2.46.0-1
-dev-libs/atk-2.38.0-1
+dev-libs/atk-2.46.0-1
-dev-libs/libgusb-0.4.0-1
+dev-libs/libgusb-0.4.1-1
-sys-kernel/vanilla-sources-5.19.12-1
+sys-kernel/vanilla-sources-6.0.0-1
"""
        self.assertEqual(fixtures.console.stdout, expected)

    def test_when_left_is_none_should_use_published(self, fixtures: Fixtures):
        publisher.publish(fixtures.build1)

        status = fixtures.gbpcli("gbp diff lighthouse")

        self.assertEqual(status, 0)
        expected = """$ gbp diff lighthouse
diff -r lighthouse/3111 lighthouse/3112
--- lighthouse/3111 Sun Oct  2 12:10:02 2022 -0700
+++ lighthouse/3112 Mon Oct  3 04:38:28 2022 -0700
-app-accessibility/at-spi2-atk-2.38.0-1
+app-accessibility/at-spi2-atk-2.46.0-1
-app-accessibility/at-spi2-core-2.44.1-1
+app-accessibility/at-spi2-core-2.46.0-1
-dev-libs/atk-2.38.0-1
+dev-libs/atk-2.46.0-1
-dev-libs/libgusb-0.4.0-1
+dev-libs/libgusb-0.4.1-1
-sys-kernel/vanilla-sources-5.19.12-1
+sys-kernel/vanilla-sources-6.0.0-1
"""
        self.assertEqual(fixtures.console.stdout, expected)

    def test_when_left_is_none_and_not_published(self, fixtures: Fixtures):
        status = fixtures.gbpcli("gbp diff lighthouse")

        self.assertEqual(status, 1)
        self.assertEqual(
            fixtures.console.stderr, "No builds given and no builds published\n"
        )

    def test_against_missing_timestamps(self, fixtures: Fixtures):
        # Legacy builds have no (None) built field
        publisher.save(fixtures.build1, built=None)

        status = fixtures.gbpcli("gbp diff lighthouse 3111 3112")

        self.assertEqual(status, 0)
        self.assertEqual(
            fixtures.console.stdout,
            """$ gbp diff lighthouse 3111 3112
diff -r lighthouse/3111 lighthouse/3112
--- lighthouse/3111 Sat Mar 20 11:57:21 2021 -0700
+++ lighthouse/3112 Mon Oct  3 04:38:28 2022 -0700
-app-accessibility/at-spi2-atk-2.38.0-1
+app-accessibility/at-spi2-atk-2.46.0-1
-app-accessibility/at-spi2-core-2.44.1-1
+app-accessibility/at-spi2-core-2.46.0-1
-dev-libs/atk-2.38.0-1
+dev-libs/atk-2.46.0-1
-dev-libs/libgusb-0.4.0-1
+dev-libs/libgusb-0.4.1-1
-sys-kernel/vanilla-sources-5.19.12-1
+sys-kernel/vanilla-sources-6.0.0-1
""",
        )

    def test_left_and_right_equal(self, fixtures: Fixtures) -> None:
        cmdline = "gbp diff lighthouse 3111 3111"
        fixtures.gbpcli(cmdline)

        self.assertEqual(fixtures.console.stdout, f"$ {cmdline}\n")
