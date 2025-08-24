"""Tests for the latest subcommand"""

# pylint: disable=missing-docstring
from unittest import TestCase

import gbp_testkit.fixtures as testkit
from unittest_fixtures import Fixtures, given

from . import lib


@given(testkit.gbpcli, lib.pulled_build)
class LatestTestCase(TestCase):
    """latest() tests"""

    def test(self, fixtures: Fixtures):
        status = fixtures.gbpcli("gbp latest babette")

        self.assertEqual(status, 0)
        expected = f"$ gbp latest babette\n{fixtures.build.build_id}\n"
        self.assertEqual(fixtures.console.stdout, expected)

    def test_should_print_error_when_not_found(self, fixtures: Fixtures):
        status = fixtures.gbpcli("gbp latest bogus")

        self.assertEqual(status, 1)
        self.assertEqual(
            fixtures.console.stderr, "No builds exist for the given machine\n"
        )
