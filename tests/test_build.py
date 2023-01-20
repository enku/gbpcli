"""Tests for the build subcommand"""
# pylint: disable=missing-function-docstring
from argparse import Namespace

from gbpcli import queries
from gbpcli.subcommands.build import handler as build

from . import TestCase


class MachinesTestCase(TestCase):
    """machines() tests"""

    def test(self):
        args = Namespace(machine="babette")
        self.make_response("schedule_build.json")

        status = build(args, self.gbp, self.console, self.errorf)

        self.assertEqual(status, 0)
        self.assertEqual(self.console.getvalue(), "")
        self.assert_graphql(queries.schedule_build, machine="babette")
