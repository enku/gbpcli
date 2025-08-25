"""Tests for the publish subcommand"""

# pylint: disable=missing-docstring
from unittest import TestCase

import gbp_testkit.fixtures as testkit
from gentoo_build_publisher import publisher
from gentoo_build_publisher.types import Build
from unittest_fixtures import Fixtures, given


@given(testkit.gbpcli, testkit.publisher)
class PublishTestCase(TestCase):
    """publish() tests"""

    def test(self, fixtures: Fixtures):
        build = Build(machine="lighthouse", build_id="3109")
        publisher.pull(build)

        self.assertFalse(publisher.published(build))
        fixtures.gbpcli("gbp publish lighthouse 3109")

        self.assertTrue(publisher.published(build))

    def test_should_get_latest_when_number_is_none(self, fixtures: Fixtures):
        builds = [
            Build(machine="lighthouse", build_id="3109"),
            Build(machine="lighthouse", build_id="3110"),
        ]
        publisher.pull(builds[0])
        publisher.pull(builds[1])  # <- latest

        status = fixtures.gbpcli("gbp publish lighthouse")

        self.assertEqual(status, 0)
        self.assertTrue(publisher.published(builds[1]))
