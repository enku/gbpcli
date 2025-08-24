"""Tests for the packages subcommand"""

# pylint: disable=missing-docstring
from unittest import TestCase

import gbp_testkit.fixtures as testkit
from gentoo_build_publisher import publisher
from unittest_fixtures import Fixtures, given, where

from . import lib

PACKAGES = [
    "app-portage/gentoolkit-0.5.1-r1",
    "dev-perl/Pod-Parser-1.630.0-r1",
    "media-libs/harfbuzz-2.9.1",
    "x11-libs/cairo-1.16.0-r4",
]


@given(testkit.gbpcli, lib.pulled_build)
@where(pulled_build__packages=PACKAGES)
class PackagesTestCase(TestCase):
    """packages() tests"""

    def test(self, fixtures: Fixtures):
        build = fixtures.build
        cmdline = f"gbp packages {build.machine} {build.build_id}"

        status = fixtures.gbpcli(cmdline)

        self.assertEqual(status, 0)
        expected = (
            f"$ {cmdline}\n"
            + "\n".join(p.cpv for p in publisher.get_packages(build))
            + "\n"
        )
        self.assertEqual(fixtures.console.stdout, expected)

    def test_with_build_ids(self, fixtures: Fixtures):
        build = fixtures.build
        cmdline = f"gbp packages -b {build.machine} {build.build_id}"

        status = fixtures.gbpcli(cmdline)

        self.assertEqual(status, 0)
        expected = (
            f"$ {cmdline}\n"
            + "\n".join(p.cpvb() for p in publisher.get_packages(build))
            + "\n"
        )
        self.assertEqual(fixtures.console.stdout, expected)

    def test_when_build_does_not_exist_prints_error(self, fixtures: Fixtures):
        status = fixtures.gbpcli("gbp packages bogus 268")

        self.assertEqual(status, 1)
        self.assertEqual(fixtures.console.stderr, "Not Found\n")
