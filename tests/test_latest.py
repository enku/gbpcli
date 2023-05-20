"""Tests for the latest subcommand"""
# pylint: disable=missing-function-docstring,protected-access
from argparse import Namespace
from unittest import mock

from gbpcli.subcommands.latest import handler as latest

from . import LOCAL_TIMEZONE, TestCase


@mock.patch("gbpcli.render.LOCAL_TIMEZONE", new=LOCAL_TIMEZONE)
class LatestTestCase(TestCase):
    """latest() tests"""

    def test(self):
        args = Namespace(machine="lighthouse")
        self.make_response("latest.json")

        status = latest(args, self.gbp, self.console)

        self.assertEqual(status, 0)
        expected = "3113\n"
        self.assertEqual(self.console.out.getvalue(), expected)
        self.assert_graphql(self.gbp.query.latest, machine="lighthouse")

    def test_should_print_error_when_not_found(self):
        args = Namespace(machine="bogus")
        self.make_response({"data": {"latest": None}})

        status = latest(args, self.gbp, self.console)

        self.assertEqual(status, 1)
        self.assertEqual(
            self.console.err.getvalue(), "No builds exist for the given machine\n"
        )
