"""Tests for the build subcommand"""
# pylint: disable=missing-function-docstring,protected-access
from argparse import Namespace

from gbpcli.subcommands.build import handler as build

from . import TestCase


class MachinesTestCase(TestCase):
    """machines() tests"""

    def test(self):
        args = Namespace(machine="babette")
        self.make_response("schedule_build.json")

        status = build(args, self.gbp, self.out, self.err)

        self.assertEqual(status, 0)
        self.assertEqual(self.out.getvalue(), "")
        self.assert_graphql(self.gbp.query.schedule_build, machine="babette")
