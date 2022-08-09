"""Tests for the keep subcommand"""
# pylint: disable=missing-function-docstring
from argparse import Namespace

from gbpcli import queries
from gbpcli.subcommands.keep import handler as keep

from . import TestCase, mock_print


class KeepTestCase(TestCase):
    """keep() tests"""

    maxDiff = None

    def test_keep(self):
        args = Namespace(machine="lighthouse", number="3210", release=False)
        self.make_response("keep_build.json")

        status = keep(args, self.gbp, self.console)

        self.assertEqual(status, 0)
        self.assert_graphql(queries.keep_build, id="lighthouse.3210")

    @mock_print("gbpcli.subcommands.keep")
    def test_keep_should_print_error_when_build_does_not_exist(self, print_mock):
        args = Namespace(machine="lighthouse", number="3210", release=False)
        self.make_response({"data": {"keepBuild": None}})

        status = keep(args, self.gbp, self.console)
        self.assertEqual(status, 1)
        self.assertEqual(print_mock.stderr.getvalue(), "Not Found\n")

    def test_release(self):
        args = Namespace(machine="lighthouse", number="3210", release=True)
        self.make_response("release_build.json")

        status = keep(args, self.gbp, self.console)

        self.assertEqual(status, 0)
        self.assert_graphql(queries.release_build, id="lighthouse.3210")

    @mock_print("gbpcli.subcommands.keep")
    def test_release_should_print_error_when_build_does_not_exist(self, print_mock):
        args = Namespace(machine="lighthouse", number="3210", release=True)
        self.make_response({"data": {"releaseBuild": None}})

        status = keep(args, self.gbp, self.console)
        self.assertEqual(status, 1)
        self.assertEqual(print_mock.stderr.getvalue(), "Not Found\n")
