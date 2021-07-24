"""Tests for the machines subcommand"""
# pylint: disable=missing-function-docstring
import unittest
from argparse import Namespace
from json import loads as parse
from unittest import mock

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
        gbp.session.get.return_value = make_response(json=mock_json)

        status = machines(args, gbp)

        self.assertEqual(status, 0)
        self.assertEqual(print_mock.stdout.getvalue(), EXPECTED_OUTPUT)
        gbp.session.get.assert_called_once_with("http://test.invalid/api/machines/")


EXPECTED_OUTPUT = """\
babette          14
base             12
blackwidow       57
gbp              57
git               4
gnome-desktop    56
jenkins           7
lighthouse       57
pgadmin           7
postgres          7
rabbitmq          8
registry         14
teamplayer        1
testing          57
web              16
"""
