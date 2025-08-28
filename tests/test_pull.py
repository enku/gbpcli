"""Tests for the pull subcommand"""

# pylint: disable=missing-docstring
from unittest import TestCase

import gbp_testkit.fixtures as testkit
from gentoo_build_publisher import publisher
from gentoo_build_publisher.types import Build
from unittest_fixtures import Fixtures, given

BUILD = Build(machine="lighthouse", build_id="3226")


@given(testkit.gbpcli)
class PullTestCase(TestCase):
    """pull() tests"""

    def test(self, fixtures: Fixtures):
        cmdline = "gbp pull lighthouse 3226"

        fixtures.gbpcli(cmdline)

        self.assertTrue(publisher.pulled(BUILD))

    def test_with_note(self, fixtures: Fixtures) -> None:
        cmdline = "gbp pull lighthouse 3226 --note='This is a test'"

        fixtures.gbpcli(cmdline)

        record = publisher.record(BUILD)
        self.assertEqual(record.note, "This is a test")

    def test_with_tags(self, fixtures: Fixtures) -> None:
        cmdline = "gbp pull lighthouse 3226 --tag test"

        fixtures.gbpcli(cmdline)

        self.assertEqual(publisher.tags(BUILD), ["test"])
