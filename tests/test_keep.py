"""Tests for the keep subcommand"""

# pylint: disable=missing-function-docstring,protected-access
from argparse import Namespace

from unittest_fixtures import requires

from gbpcli.subcommands.keep import handler as keep

from . import TestCase, make_response


@requires("gbp", "console")
class KeepTestCase(TestCase):
    """keep() tests"""

    maxDiff = None

    def test_keep(self):
        args = Namespace(machine="lighthouse", number="3210", release=False)
        gbp = self.fixtures.gbp
        console = self.fixtures.console
        make_response(gbp, "keep_build.json")

        status = keep(args, gbp, console)

        self.assertEqual(status, 0)
        self.assert_graphql(gbp, gbp.query.gbpcli.keep_build, id="lighthouse.3210")

    def test_keep_should_print_error_when_build_does_not_exist(self):
        args = Namespace(machine="lighthouse", number="3210", release=False)
        gbp = self.fixtures.gbp
        console = self.fixtures.console
        make_response(gbp, {"data": {"keepBuild": None}})

        status = keep(args, gbp, console)
        self.assertEqual(status, 1)
        self.assertEqual(console.err.file.getvalue(), "Not Found\n")

    def test_release(self):
        args = Namespace(machine="lighthouse", number="3210", release=True)
        gbp = self.fixtures.gbp
        console = self.fixtures.console
        make_response(gbp, "release_build.json")

        status = keep(args, gbp, console)

        self.assertEqual(status, 0)
        self.assert_graphql(gbp, gbp.query.gbpcli.release_build, id="lighthouse.3210")

    def test_release_should_print_error_when_build_does_not_exist(self):
        args = Namespace(machine="lighthouse", number="3210", release=True)
        gbp = self.fixtures.gbp
        console = self.fixtures.console
        make_response(gbp, {"data": {"releaseBuild": None}})

        status = keep(args, gbp, console)

        self.assertEqual(status, 1)
        self.assertEqual(console.err.file.getvalue(), "Not Found\n")
