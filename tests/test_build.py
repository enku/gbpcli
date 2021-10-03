"""Tests for the build subcommand"""
# pylint: disable=missing-function-docstring
import unittest
from argparse import Namespace
from json import loads as parse

from gbpcli import queries
from gbpcli.subcommands.build import handler as build

from . import load_data, make_gbp, make_response, mock_print


class MachinesTestCase(unittest.TestCase):
    """machines() tests"""

    @mock_print("gbpcli.subcommands.build")
    def test(self, print_mock):
        args = Namespace(machine="babette")
        mock_json = parse(load_data("schedule_build.json"))
        gbp = make_gbp()
        gbp.session.post.return_value = make_response(json=mock_json)

        status = build(args, gbp)

        self.assertEqual(status, 0)
        self.assertEqual(print_mock.stdout.getvalue(), "")
        gbp.session.post.assert_called_once_with(
            gbp.url,
            json={"query": queries.schedule_build, "variables": {"name": "babette"}},
            headers=gbp.headers,
        )
