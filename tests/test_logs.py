"""Tests for the logs subcommand"""

# pylint: disable=missing-docstring
from unittest import TestCase

import gbp_testkit.fixtures as testkit
from unittest_fixtures import Fixtures, given, where

from . import lib


@given(testkit.gbpcli, lib.pulled_build)
@where(pulled_build__logs="This is a test!")
class LogsTestCase(TestCase):
    """logs() tests"""

    def test(self, fixtures: Fixtures):
        build = fixtures.build

        status = fixtures.gbpcli(f"gbp logs {build.machine} {build.build_id}")

        self.assertEqual(status, 0)
        self.assertEqual(
            fixtures.console.stdout,
            f"$ gbp logs {build.machine} {build.build_id}\nThis is a test!\n",
        )

    def test_should_print_error_when_logs_dont_exist(self, fixtures: Fixtures):
        status = fixtures.gbpcli("gbp logs lighthouse 9999")

        self.assertEqual(fixtures.console.stderr, "Not Found\n")
        self.assertEqual(status, 1)

    def test_search_logs(self, fixtures: Fixtures):
        build = fixtures.build
        cmdline = f"gbp logs -s {build.machine} test"

        status = fixtures.gbpcli(cmdline)

        self.assertEqual(status, 0, fixtures.console.stderr)
        expected = f"$ {cmdline}\n{build.machine}/{build.build_id}\nThis is a test!\n"
        self.assertEqual(fixtures.console.stdout, expected)

    def test_search_no_matches(self, fixtures: Fixtures) -> None:
        build = fixtures.build
        cmdline = f"gbp logs -s {build.machine} bogus"

        status = fixtures.gbpcli(cmdline)

        self.assertEqual(status, 1)
        expected = "No matches found\n"
        self.assertEqual(fixtures.console.stderr, expected)
