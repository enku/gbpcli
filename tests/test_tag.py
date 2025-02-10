"""Tests for the tag subcommand"""

# pylint: disable=missing-docstring,protected-access
from unittest_fixtures import requires

from gbpcli.subcommands.tag import handler as tag

from . import TestCase, make_response, parse_args


@requires("gbp", "console")
class TagTestCase(TestCase):
    """tag() tests"""

    def test_tag(self):
        cmdline = "gbp tag lighthouse 9400 prod"
        args = parse_args(cmdline)
        gbp = self.fixtures.gbp
        make_response(gbp, "tag_build.json")

        status = tag(args, gbp, self.fixtures.console)

        self.assertEqual(status, 0)
        self.assert_graphql(
            gbp, gbp.query.gbpcli.tag_build, id="lighthouse.9400", tag="prod"
        )

    def test_untag(self):
        cmdline = "gbp tag -r lighthouse prod"
        args = parse_args(cmdline)
        gbp = self.fixtures.gbp
        make_response(gbp, "untag_build.json")

        status = tag(args, gbp, self.fixtures.console)

        self.assertEqual(status, 0)
        self.assert_graphql(
            gbp, gbp.query.gbpcli.untag_build, machine="lighthouse", tag="prod"
        )

    def test_untag_with_string_starting_with_tagsym_works(self):
        cmdline = "gbp tag -r lighthouse @prod"
        args = parse_args(cmdline)
        gbp = self.fixtures.gbp
        make_response(gbp, "untag_build.json")

        status = tag(args, gbp, self.fixtures.console)

        self.assertEqual(status, 0)
        self.assert_graphql(
            gbp, gbp.query.gbpcli.untag_build, machine="lighthouse", tag="prod"
        )

    def test_untag_with_build_number_gives_error(self):
        cmdline = "gbp tag -r lighthouse 9400 prod"
        args = parse_args(cmdline)
        gbp = self.fixtures.gbp

        status = tag(args, gbp, self.fixtures.console)

        self.assertEqual(status, 1)
        self.assertEqual(
            self.fixtures.console.err.file.getvalue(),
            "When removing a tag, omit the build number\n",
        )
