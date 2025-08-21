"""Tests for the publish subcommand"""

# pylint: disable=missing-function-docstring,protected-access
import gbp_testkit.fixtures as testkit
from gbp_testkit.helpers import parse_args
from gentoo_build_publisher import publisher
from gentoo_build_publisher.types import Build
from unittest_fixtures import Fixtures, given

from gbpcli.subcommands.publish import handler as publish

from . import lib


@given(testkit.gbp, testkit.console, lib.local_timezone, testkit.publisher)
class PublishTestCase(lib.TestCase):
    """publish() tests"""

    def test(self, fixtures: Fixtures):
        build = Build(machine="lighthouse", build_id="3109")
        publisher.pull(build)
        cmdline = "gbp publish lighthouse 3109"
        args = parse_args(cmdline)
        gbp = fixtures.gbp
        console = fixtures.console

        self.assertFalse(publisher.published(build))
        publish(args, gbp, console)

        self.assertTrue(publisher.published(build))

    def test_should_get_latest_when_number_is_none(self, fixtures: Fixtures):
        builds = [
            Build(machine="lighthouse", build_id="3109"),
            Build(machine="lighthouse", build_id="3110"),
        ]
        publisher.pull(builds[0])
        publisher.pull(builds[1])  # <- latest
        cmdline = "gbp publish lighthouse"
        args = parse_args(cmdline)
        gbp = fixtures.gbp
        console = fixtures.console

        status = publish(args, gbp, console)

        self.assertEqual(status, 0)
        self.assertTrue(publisher.published(builds[1]))
