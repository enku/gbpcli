"""Tests for the keep subcommand"""

# pylint: disable=missing-function-docstring,protected-access
from gbp_testkit.helpers import parse_args
from unittest_fixtures import Fixtures, given

from gbpcli.subcommands.keep import handler as keep

from . import TestCase, make_response


@given("gbp", "console")
class KeepTestCase(TestCase):
    """keep() tests"""

    def test_keep(self, fixtures: Fixtures):
        cmdline = "gbp keep lighthouse 3210"
        args = parse_args(cmdline)
        gbp = fixtures.gbp
        console = fixtures.console
        make_response(gbp, "keep_build.json")

        status = keep(args, gbp, console)

        self.assertEqual(status, 0)
        self.assert_graphql(gbp, gbp.query.gbpcli.keep_build, id="lighthouse.3210")

    def test_keep_should_print_error_when_build_does_not_exist(
        self, fixtures: Fixtures
    ):
        cmdline = "gbp keep lighthouse 3210"
        args = parse_args(cmdline)
        gbp = fixtures.gbp
        console = fixtures.console
        make_response(gbp, {"data": {"keepBuild": None}})

        status = keep(args, gbp, console)
        self.assertEqual(status, 1)
        self.assertEqual(console.err.file.getvalue(), "Not Found\n")

    def test_release(self, fixtures: Fixtures):
        cmdline = "gbp keep -r lighthouse 3210"
        args = parse_args(cmdline)
        gbp = fixtures.gbp
        console = fixtures.console
        make_response(gbp, "release_build.json")

        status = keep(args, gbp, console)

        self.assertEqual(status, 0)
        self.assert_graphql(gbp, gbp.query.gbpcli.release_build, id="lighthouse.3210")

    def test_release_should_print_error_when_build_does_not_exist(
        self, fixtures: Fixtures
    ):
        cmdline = "gbp keep -r lighthouse 3210"
        args = parse_args(cmdline)
        gbp = fixtures.gbp
        console = fixtures.console
        make_response(gbp, {"data": {"releaseBuild": None}})

        status = keep(args, gbp, console)

        self.assertEqual(status, 1)
        self.assertEqual(console.err.file.getvalue(), "Not Found\n")
