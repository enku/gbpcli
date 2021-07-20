"""Tests for the show subcommand"""
# pylint: disable=missing-function-docstring
import io
import sys
import unittest
from functools import partial
from json import loads as parse
from unittest import mock

from gbpcli.subcommands.show import handler as show

from . import LOCAL_TIMEZONE, load_data, make_response


@mock.patch("gbpcli.LOCAL_TIMEZONE", new=LOCAL_TIMEZONE)
@mock.patch("gbpcli.subcommands.show.print")
class ShowTestCase(unittest.TestCase):
    """show() tests"""

    def test(self, print_mock):
        stdout = io.StringIO()
        print_mock.side_effect = partial(print, file=stdout)
        args_mock = mock.Mock(
            url="http://test.invalid/", machine="lighthouse", number=2080
        )
        mock_json = parse(load_data("show.json"))
        args_mock.session.get.return_value = make_response(json=mock_json)

        show(args_mock)

        expected = """\
Build: lighthouse/2080
Submitted: Tue Jul 20 14:39:45 2021 -0700
Completed: Tue Jul 20 14:47:45 2021 -0700
Published: yes
Keep: no

    Packages built:
    
    * acct-group/nm-openvpn-0-1
    * acct-user/nm-openvpn-0-1
    * net-vpn/networkmanager-openvpn-1.8.12-r1-1
    * sys-kernel/gentoo-sources-5.13.4-1
"""
        self.assertEqual(stdout.getvalue(), expected)
        args_mock.session.get.assert_called_once_with(
            "http://test.invalid/api/builds/lighthouse/2080"
        )

    def test_should_get_latest_when_number_is_0(self, _print_mock):
        args_mock = mock.Mock(
            url="http://test.invalid/", machine="lighthouse", number=0
        )
        mock_latest = make_response(json={"error": None, "number": 2080})
        mock_json = parse(load_data("show.json"))
        args_mock.session.get.side_effect = (mock_latest, make_response(json=mock_json))

        status = show(args_mock)

        expected_calls = [
            mock.call("http://test.invalid/api/builds/lighthouse/latest"),
            mock.call("http://test.invalid/api/builds/lighthouse/2080"),
        ]
        args_mock.session.get.has_calls(expected_calls)
        self.assertEqual(status, 0)

    def test_should_print_error_when_build_does_not_exist(self, print_mock):
        args_mock = mock.Mock(url="http://test.invalid/", machine="bogus", number=934)
        args_mock.session.get.return_value = make_response(status_code=404)

        status = show(args_mock)

        print_mock.assert_called_once_with("Build not found", file=sys.stderr)
        self.assertEqual(status, 1)
