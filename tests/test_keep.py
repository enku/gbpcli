"""Tests for the keep subcommand"""

# pylint: disable=missing-function-docstring
from unittest import TestCase

import gbp_testkit.fixtures as testkit
from gentoo_build_publisher import publisher
from unittest_fixtures import Fixtures, given

from . import lib


@given(testkit.gbpcli, lib.pulled_build)
class KeepTestCase(TestCase):
    """keep() tests"""

    def test_keep(self, fixtures: Fixtures):
        build = fixtures.build

        status = fixtures.gbpcli(f"gbp keep {build.machine} {build.build_id}")

        self.assertEqual(status, 0)
        self.assertTrue(publisher.record(build).keep)

    def test_keep_should_print_error_when_build_does_not_exist(
        self, fixtures: Fixtures
    ):
        status = fixtures.gbpcli("gbp keep bogus 9000")

        self.assertEqual(status, 1)
        self.assertEqual(fixtures.console.stderr, "Not Found\n")

    def test_release(self, fixtures: Fixtures):
        build = publisher.save(fixtures.pulled_build, keep=True)

        status = fixtures.gbpcli(f"gbp keep -r {build.machine} {build.build_id}")

        self.assertEqual(status, 0)
        self.assertFalse(publisher.record(fixtures.build).keep)

    def test_release_should_print_error_when_build_does_not_exist(
        self, fixtures: Fixtures
    ):
        status = fixtures.gbpcli("gbp keep -r bogus 9000")

        self.assertEqual(status, 1)
        self.assertEqual(fixtures.console.stderr, "Not Found\n")
