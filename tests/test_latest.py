"""Tests for the latest subcommand"""

# pylint: disable=missing-function-docstring,protected-access
from argparse import Namespace
from unittest import mock

from unittest_fixtures import requires

from gbpcli.subcommands.latest import handler as latest

from . import LOCAL_TIMEZONE, TestCase, make_response


@requires("gbp", "console")
@mock.patch("gbpcli.render.LOCAL_TIMEZONE", new=LOCAL_TIMEZONE)
class LatestTestCase(TestCase):
    """latest() tests"""

    def test(self):
        args = Namespace(machine="lighthouse")
        gbp = self.fixtures.gbp
        console = self.fixtures.console
        make_response(gbp, "latest.json")

        status = latest(args, gbp, console)

        self.assertEqual(status, 0)
        expected = "3113\n"
        self.assertEqual(console.out.getvalue(), expected)
        self.assert_graphql(gbp, gbp.query.gbpcli.latest, machine="lighthouse")

    def test_should_print_error_when_not_found(self):
        args = Namespace(machine="bogus")
        gbp = self.fixtures.gbp
        console = self.fixtures.console
        make_response(gbp, {"data": {"latest": None}})

        status = latest(args, gbp, console)

        self.assertEqual(status, 1)
        self.assertEqual(
            self.fixtures.console.err.getvalue(),
            "No builds exist for the given machine\n",
        )
