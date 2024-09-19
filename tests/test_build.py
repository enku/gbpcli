"""Tests for the build subcommand"""

# pylint: disable=missing-function-docstring,protected-access
from argparse import Namespace

from unittest_fixtures import requires

from gbpcli.subcommands.build import handler as build

from . import TestCase, make_response


@requires("gbp", "console")
class MachinesTestCase(TestCase):
    """machines() tests"""

    def test(self) -> None:
        gbp = self.fixtures.gbp
        args = Namespace(machine="babette", param=None)
        make_response(gbp, "schedule_build.json")

        status = build(args, gbp, self.fixtures.console)

        self.assertEqual(status, 0)
        self.assertEqual(self.fixtures.console.out.getvalue(), "")
        self.assert_graphql(
            gbp, gbp.query.gbpcli.schedule_build, machine="babette", params=[]
        )

    def test_with_build_params(self) -> None:
        gbp = self.fixtures.gbp
        console = self.fixtures.console
        args = Namespace(machine="babette", param=["BUILD_TARGET=emptytree"])
        make_response(gbp, "schedule_build.json")

        status = build(args, gbp, console)

        self.assertEqual(status, 0)
        self.assertEqual(console.out.getvalue(), "")
        self.assert_graphql(
            gbp,
            gbp.query.gbpcli.schedule_build,
            machine="babette",
            params=[{"name": "BUILD_TARGET", "value": "emptytree"}],
        )
        self.assert_graphql(
            gbp,
            gbp.query.gbpcli.schedule_build,
            machine="babette",
            params=[{"name": "BUILD_TARGET", "value": "emptytree"}],
        )

    def test_when_build_param_missing_equals_sign(self) -> None:
        args = Namespace(machine="babette", param=["BUILD_TARGETemptytree"])
        make_response(self.fixtures.gbp, "schedule_build.json")

        status = build(args, self.fixtures.gbp, self.fixtures.console)

        self.assertEqual(status, 1)
        error_msg = "Build parameters must be of the format name=value\n"
        self.assertEqual(self.fixtures.console.err.getvalue(), error_msg)

    def test_with_repo(self) -> None:
        gbp = self.fixtures.gbp
        console = self.fixtures.console
        args = Namespace(machine="gentoo", param=None, is_repo=True)
        make_response(gbp, "schedule_build.json")

        status = build(args, gbp, console)

        self.assertEqual(status, 0)
        self.assertEqual(console.out.getvalue(), "")
        self.assert_graphql(
            gbp,
            gbp.query.gbpcli.schedule_build,
            machine="gentoo",
            isRepo=True,
            params=[],
        )
