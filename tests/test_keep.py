"""Tests for the keep subcommand"""
# pylint: disable=missing-function-docstring,protected-access
from argparse import Namespace

from gbpcli.subcommands.keep import handler as keep

from . import TestCase


class KeepTestCase(TestCase):
    """keep() tests"""

    maxDiff = None

    def test_keep(self):
        args = Namespace(machine="lighthouse", number="3210", release=False)
        self.make_response("keep_build.json")

        status = keep(args, self.gbp, self.console)

        self.assertEqual(status, 0)
        self.assert_graphql(self.gbp.query.keep_build, id="lighthouse.3210")

    def test_keep_should_print_error_when_build_does_not_exist(self):
        args = Namespace(machine="lighthouse", number="3210", release=False)
        self.make_response({"data": {"keepBuild": None}})

        status = keep(args, self.gbp, self.console)
        self.assertEqual(status, 1)
        self.assertEqual(self.console.err.getvalue(), "Not Found\n")

    def test_release(self):
        args = Namespace(machine="lighthouse", number="3210", release=True)
        self.make_response("release_build.json")

        status = keep(args, self.gbp, self.console)

        self.assertEqual(status, 0)
        self.assert_graphql(self.gbp.query.release_build, id="lighthouse.3210")

    def test_release_should_print_error_when_build_does_not_exist(self):
        args = Namespace(machine="lighthouse", number="3210", release=True)
        self.make_response({"data": {"releaseBuild": None}})

        status = keep(args, self.gbp, self.console)
        self.assertEqual(status, 1)
        self.assertEqual(self.console.err.getvalue(), "Not Found\n")
