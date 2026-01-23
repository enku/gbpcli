"""Tests for the diff subcommand"""

# pylint: disable=missing-function-docstring,protected-access
from unittest import TestCase

import gbp_testkit.fixtures as testkit
from gbp_testkit.helpers import LOCAL_TIMEZONE, ts
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
@where(build2__built=ts("2022-10-03 11:38:28"))
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
@where(build1__built=ts("2022-10-02 19:10:02"))
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


@given(right=lib.pulled_build)
@where(right__build=Build(machine="mediaserver", build_id="6323"))
@where(
    right__packages=[
        "app-alternatives/gpg-1-r2",
        "app-crypt/gpgme-2.0.1",
        "dev-libs/glib-2.84.4",
        "dev-perl/File-Slurper-0.14.0-r1",
        "sys-apps/locale-gen-3.9",
        "sys-libs/glibc-2.42-r2",
    ]
)
@where(right__built=ts("2025-10-30 11:55:35"))
@given(left=lib.pulled_build)
@where(left__build=Build(machine="mediaserver", build_id="6322"))
@where(
    left__packages=[
        "app-alternatives/gpg-1-r2",
        "app-crypt/gpgme-2.0.1",
        "dev-perl/File-Slurper-0.14.0",
        "sys-apps/locale-gen-3.8",
        "sys-libs/glibc-2.42-r1",
        "sys-libs/libcap-2.77",
    ]
)
@where(left__built=ts("2025-10-29 11:55:32"))
@given(local_timezone=testkit.patch)
@where(local_timezone__target="gbpcli.render.LOCAL_TIMEZONE")
@where(local_timezone__new=LOCAL_TIMEZONE)
@given(testkit.gbpcli)
class DiffStatTests(TestCase):
    """tests for `gbp diff --stat`"""

    def test(self, fixtures: Fixtures) -> None:
        status = fixtures.gbpcli("gbp diff --stat mediaserver 6322 6323")
        self.assertEqual(status, 0)
        self.assertEqual(
            fixtures.console.stdout,
            """\
$ gbp diff --stat mediaserver 6322 6323
diff -r mediaserver/6322 mediaserver/6323
--- mediaserver/6322 Wed Oct 29 04:55:32 2025 -0700
+++ mediaserver/6323 Thu Oct 30 04:55:35 2025 -0700
-app-alternatives/gpg-1-r2-1
+app-alternatives/gpg-1-r2-2
-app-crypt/gpgme-2.0.1-1
+app-crypt/gpgme-2.0.1-2
+dev-libs/glib-2.84.4-1
-dev-perl/File-Slurper-0.14.0-1
+dev-perl/File-Slurper-0.14.0-r1-1
-sys-apps/locale-gen-3.8-1
+sys-apps/locale-gen-3.9-1
-sys-libs/glibc-2.42-r1-1
+sys-libs/glibc-2.42-r2-1

6 packages added (3 upgrades, 1 new, 2 reinstalls), Size of downloads: 4 KiB
5 packages removed
""",
        )
