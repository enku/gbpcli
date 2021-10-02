"""Tests for the machines subcommand"""
# pylint: disable=missing-function-docstring
import unittest
from argparse import Namespace
from json import loads as parse
from unittest import mock

from gbpcli import queries
from gbpcli.subcommands.machines import handler as machines

from . import LOCAL_TIMEZONE, load_data, make_gbp, make_response, mock_print


@mock.patch("gbpcli.LOCAL_TIMEZONE", new=LOCAL_TIMEZONE)
class MachinesTestCase(unittest.TestCase):
    """machines() tests"""

    @mock_print("gbpcli.subcommands.machines")
    def test(self, print_mock):
        args = Namespace()
        mock_json = parse(load_data("machines.json"))
        gbp = make_gbp()
        gbp.session.post.return_value = make_response(json=mock_json)

        status = machines(args, gbp)

        self.assertEqual(status, 0)
        self.assertEqual(print_mock.stdout.getvalue(), EXPECTED_OUTPUT)
        gbp.session.post.assert_called_once_with(
            gbp.url,
            json={"query": queries.machines, "variables": None},
            headers=gbp.headers,
        )


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
