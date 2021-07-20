"""Tests for the machines subcommand"""
# pylint: disable=missing-function-docstring
import io
import unittest
from functools import partial
from json import loads as parse
from unittest import mock

from gbpcli.subcommands.machines import handler as machines

from . import LOCAL_TIMEZONE, load_data, make_response


@mock.patch("gbpcli.LOCAL_TIMEZONE", new=LOCAL_TIMEZONE)
@mock.patch("gbpcli.subcommands.machines.print")
class MachinesTestCase(unittest.TestCase):
    """machines() tests"""

    def test(self, print_mock):
        stdout = io.StringIO()
        print_mock.side_effect = partial(print, file=stdout)
        args_mock = mock.Mock(url="http://test.invalid/")
        mock_json = parse(load_data("machines.json"))
        args_mock.session.get.return_value = make_response(json=mock_json)

        machines(args_mock)

        self.assertEqual(stdout.getvalue(), EXPECTED_OUTPUT)
        args_mock.session.get.assert_called_once_with(
            "http://test.invalid/api/machines/"
        )


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
