"""Tests for the build subcommand"""
# pylint: disable=missing-function-docstring,protected-access
from argparse import Namespace

from gbpcli.subcommands.build import handler as build

from . import TestCase


class MachinesTestCase(TestCase):
    """machines() tests"""

    def test(self) -> None:
        args = Namespace(machine="babette", param=None)
        self.make_response("schedule_build.json")

        status = build(args, self.gbp, self.console)

        self.assertEqual(status, 0)
        self.assertEqual(self.console.out.getvalue(), "")
        self.assert_graphql(
            self.gbp.query.gbpcli.schedule_build, machine="babette", params=[]
        )

    def test_with_build_params(self) -> None:
        args = Namespace(machine="babette", param=["BUILD_TARGET=emptytree"])
        self.make_response("schedule_build.json")

        status = build(args, self.gbp, self.console)

        self.assertEqual(status, 0)
        self.assertEqual(self.console.out.getvalue(), "")
        self.assert_graphql(
            self.gbp.query.gbpcli.schedule_build,
            machine="babette",
            params=[{"name": "BUILD_TARGET", "value": "emptytree"}],
        )
        self.assert_graphql(
            self.gbp.query.gbpcli.schedule_build,
            machine="babette",
            params=[{"name": "BUILD_TARGET", "value": "emptytree"}],
        )
