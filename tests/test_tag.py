"""Tests for the tag subcommand"""

# pylint: disable=missing-docstring
from unittest import TestCase

import gbp_testkit.fixtures as testkit
from gentoo_build_publisher import publisher
from gentoo_build_publisher.types import Build
from unittest_fixtures import Fixtures, given, where

from . import lib

BUILD = Build(machine="lighthouse", build_id="9400")


@given(testkit.gbpcli, lib.pulled_build)
@where(pulled_build__build=BUILD)
class TagTestCase(TestCase):
    """tag() tests"""

    def test_tag(self, fixtures: Fixtures):
        status = fixtures.gbpcli("gbp tag lighthouse 9400 prod")

        self.assertEqual(status, 0)
        self.assertEqual(publisher.tags(BUILD), ["prod"])

    def test_untag(self, fixtures: Fixtures):
        publisher.tag(BUILD, "prod")

        status = fixtures.gbpcli("gbp tag -r lighthouse prod")

        self.assertEqual(status, 0)
        self.assertEqual(publisher.tags(BUILD), [])

    def test_untag_with_string_starting_with_tagsym_works(self, fixtures: Fixtures):
        publisher.tag(BUILD, "prod")

        status = fixtures.gbpcli("gbp tag -r lighthouse @prod")

        self.assertEqual(status, 0)
        self.assertEqual(publisher.tags(BUILD), [])

    def test_untag_with_build_number_gives_error(self, fixtures: Fixtures):
        publisher.tag(BUILD, "prod")

        status = fixtures.gbpcli("gbp tag -r lighthouse 9400 prod")

        self.assertEqual(status, 1)
        self.assertEqual(
            fixtures.console.stderr, "When removing a tag, omit the build number\n"
        )
