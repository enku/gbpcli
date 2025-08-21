"""Tests for the pull subcommand"""

# pylint: disable=missing-function-docstring,protected-access
import gbp_testkit.fixtures as testkit
from gbp_testkit.helpers import parse_args
from gentoo_build_publisher import publisher
from gentoo_build_publisher.types import Build
from unittest_fixtures import Fixtures, given

from gbpcli.subcommands.pull import handler as pull

from . import lib


@given(testkit.gbp, testkit.console, lib.local_timezone)
class PullTestCase(lib.TestCase):
    """pull() tests"""

    def test(self, fixtures: Fixtures):
        build = Build(machine="lighthouse", build_id="3226")
        cmdline = "gbp pull lighthouse 3226"
        args = parse_args(cmdline)

        pull(args, fixtures.gbp, fixtures.console)

        self.assertTrue(publisher.pulled(build))

    def test_with_note(self, fixtures: Fixtures) -> None:
        build = Build(machine="lighthouse", build_id="3226")
        cmdline = "gbp pull lighthouse 3226 --note='This is a test'"
        args = parse_args(cmdline)

        pull(args, fixtures.gbp, fixtures.console)

        record = publisher.record(build)
        self.assertEqual(record.note, "This is a test")

    def test_with_tags(self, fixtures: Fixtures) -> None:
        build = Build(machine="lighthouse", build_id="3226")
        cmdline = "gbp pull lighthouse 3226 --tag test"
        args = parse_args(cmdline)

        pull(args, fixtures.gbp, fixtures.console)

        self.assertEqual(publisher.tags(build), ["test"])
