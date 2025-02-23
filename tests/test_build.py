"""Tests for the build subcommand"""

# pylint: disable=missing-function-docstring,protected-access
from gbp_testkit.helpers import parse_args
from unittest_fixtures import Fixtures, given

from gbpcli.subcommands.build import handler as build

from . import TestCase, make_response


@given("gbp", "console")
class MachinesTestCase(TestCase):
    """machines() tests"""

    def test(self, fixtures: Fixtures) -> None:
        cmdline = "gbp build babette"
        args = parse_args(cmdline)
        gbp = fixtures.gbp
        console = fixtures.console
        make_response(gbp, "schedule_build.json")

        status = build(args, gbp, console)

        self.assertEqual(status, 0)
        self.assertEqual(console.out.file.getvalue(), "")
        self.assert_graphql(
            gbp, gbp.query.gbpcli.schedule_build, machine="babette", params=[]
        )

    def test_with_build_params(self, fixtures: Fixtures) -> None:
        gbp = fixtures.gbp
        console = fixtures.console
        cmdline = "gbp build babette -p BUILD_TARGET=emptytree"
        args = parse_args(cmdline)
        make_response(gbp, "schedule_build.json")

        status = build(args, gbp, console)

        self.assertEqual(status, 0)
        self.assertEqual(console.out.file.getvalue(), "")
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

    def test_when_build_param_missing_equals_sign(self, fixtures: Fixtures) -> None:
        cmdline = "gbp build babette -p BUILD_TARGET"
        args = parse_args(cmdline)
        gbp = fixtures.gbp
        console = fixtures.console
        make_response(fixtures.gbp, "schedule_build.json")

        status = build(args, gbp, console)

        self.assertEqual(status, 1)
        error_msg = "Build parameters must be of the format name=value\n"
        self.assertEqual(console.err.file.getvalue(), error_msg)

    def test_with_repo(self, fixtures: Fixtures) -> None:
        gbp = fixtures.gbp
        console = fixtures.console
        cmdline = "gbp build -r gentoo"
        args = parse_args(cmdline)
        make_response(gbp, "schedule_build.json")

        status = build(args, gbp, console)

        self.assertEqual(status, 0)
        self.assertEqual(console.out.file.getvalue(), "")
        self.assert_graphql(
            gbp,
            gbp.query.gbpcli.schedule_build,
            machine="gentoo",
            isRepo=True,
            params=[],
        )
