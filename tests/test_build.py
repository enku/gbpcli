"""Tests for the build subcommand"""
# pylint: disable=missing-function-docstring
from argparse import Namespace

from gbpcli import queries
from gbpcli.subcommands.build import handler as build

from . import TestCase, mock_print


class MachinesTestCase(TestCase):
    """machines() tests"""

    @mock_print("gbpcli.subcommands.build")
    def test(self, _print_mock):
        args = Namespace(machine="babette")
        self.make_response("schedule_build.json")

        status = build(args, self.gbp, self.console)

        self.assertEqual(status, 0)
        self.assertEqual(self.console.getvalue(), "")
        self.assert_graphql(queries.schedule_build, machine="babette")
