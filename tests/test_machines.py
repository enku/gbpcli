"""Tests for the machines subcommand"""
# pylint: disable=missing-function-docstring
from argparse import Namespace
from unittest import mock

from gbpcli import queries
from gbpcli.subcommands.machines import handler as machines

from . import LOCAL_TIMEZONE, TestCase, mock_print


@mock.patch("gbpcli.LOCAL_TIMEZONE", new=LOCAL_TIMEZONE)
class MachinesTestCase(TestCase):
    """machines() tests"""

    @mock_print("gbpcli.subcommands.machines")
    def test(self, _print_mock):
        args = Namespace()
        self.make_response("machines.json")

        status = machines(args, self.gbp, self.console)

        self.assertEqual(status, 0)
        self.assertEqual(self.console.getvalue(), EXPECTED_OUTPUT)
        self.assert_graphql(queries.machines)


EXPECTED_OUTPUT = """\
babette          14
base             15
blackwidow       35
gbp              36
git               8
gnome-desktop    35
jenkins           9
lighthouse       35
lounge           12
pgadmin           8
postgres         12
rabbitmq          9
teamplayer        5
testing          36
web              16
"""
