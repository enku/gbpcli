"""Tests for the build subcommand"""

# pylint: disable=missing-docstring
from unittest import TestCase

import gbp_testkit.fixtures as testkit
from gentoo_build_publisher import publisher
from unittest_fixtures import Fixtures, given


@given(testkit.gbpcli, testkit.publisher)
class MachinesTestCase(TestCase):
    """machines() tests"""

    def test(self, fixtures: Fixtures) -> None:
        cmdline = "gbp build babette"
        scheduled_builds = publisher.jenkins.scheduled_builds  # type: ignore
        self.assertEqual(scheduled_builds, [])

        status = fixtures.gbpcli(cmdline)

        self.assertEqual(status, 0)
        self.assertEqual(fixtures.console.stdout, f"$ {cmdline}\n")
        self.assertEqual(scheduled_builds, [("babette", {})])

    def test_with_build_params(self, fixtures: Fixtures) -> None:
        cmdline = "gbp build babette -p BUILD_TARGET=emptytree"
        scheduled_builds = publisher.jenkins.scheduled_builds  # type: ignore

        status = fixtures.gbpcli(cmdline)

        self.assertEqual(status, 0)
        self.assertEqual(fixtures.console.stdout, f"$ {cmdline}\n")
        self.assertEqual(scheduled_builds, [("babette", {"BUILD_TARGET": "emptytree"})])

    def test_when_build_param_missing_equals_sign(self, fixtures: Fixtures) -> None:
        status = fixtures.gbpcli("gbp build babette -p BUILD_TARGET")

        self.assertEqual(status, 1)
        error_msg = "Build parameters must be of the format name=value\n"
        self.assertEqual(fixtures.console.stderr, error_msg)

    def test_with_repo(self, fixtures: Fixtures) -> None:
        scheduled_builds = publisher.jenkins.scheduled_builds  # type: ignore
        cmdline = "gbp build -r gentoo"

        status = fixtures.gbpcli(cmdline)

        self.assertEqual(status, 0)
        self.assertEqual(fixtures.console.stdout, f"$ {cmdline}\n")
        self.assertEqual(scheduled_builds, [("repos/job/gentoo", {})])
