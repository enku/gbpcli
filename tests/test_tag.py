"""Tests for the tag subcommand"""

# pylint: disable=missing-docstring,protected-access
import gbp_testkit.fixtures as testkit
from gbp_testkit.helpers import parse_args
from unittest_fixtures import Fixtures, given

from gbpcli.subcommands.tag import handler as tag

from . import lib


@given(lib.gbp, testkit.console)
class TagTestCase(lib.TestCase):
    """tag() tests"""

    def test_tag(self, fixtures: Fixtures):
        cmdline = "gbp tag lighthouse 9400 prod"
        args = parse_args(cmdline)
        gbp = fixtures.gbp
        lib.make_response(gbp, "tag_build.json")

        status = tag(args, gbp, fixtures.console)

        self.assertEqual(status, 0)
        self.assert_graphql(
            gbp, gbp.query.gbpcli.tag_build, id="lighthouse.9400", tag="prod"
        )

    def test_untag(self, fixtures: Fixtures):
        cmdline = "gbp tag -r lighthouse prod"
        args = parse_args(cmdline)
        gbp = fixtures.gbp
        lib.make_response(gbp, "untag_build.json")

        status = tag(args, gbp, fixtures.console)

        self.assertEqual(status, 0)
        self.assert_graphql(
            gbp, gbp.query.gbpcli.untag_build, machine="lighthouse", tag="prod"
        )

    def test_untag_with_string_starting_with_tagsym_works(self, fixtures: Fixtures):
        cmdline = "gbp tag -r lighthouse @prod"
        args = parse_args(cmdline)
        gbp = fixtures.gbp
        lib.make_response(gbp, "untag_build.json")

        status = tag(args, gbp, fixtures.console)

        self.assertEqual(status, 0)
        self.assert_graphql(
            gbp, gbp.query.gbpcli.untag_build, machine="lighthouse", tag="prod"
        )

    def test_untag_with_build_number_gives_error(self, fixtures: Fixtures):
        cmdline = "gbp tag -r lighthouse 9400 prod"
        args = parse_args(cmdline)
        gbp = fixtures.gbp

        status = tag(args, gbp, fixtures.console)

        self.assertEqual(status, 1)
        self.assertEqual(
            fixtures.console.err.file.getvalue(),
            "When removing a tag, omit the build number\n",
        )
