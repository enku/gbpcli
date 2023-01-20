"""Tests for the machines subcommand"""
# pylint: disable=missing-function-docstring
from argparse import Namespace
from unittest import mock

from gbpcli import queries
from gbpcli.subcommands.machines import handler as machines

from . import LOCAL_TIMEZONE, TestCase


@mock.patch("gbpcli.LOCAL_TIMEZONE", new=LOCAL_TIMEZONE)
class MachinesTestCase(TestCase):
    """machines() tests"""

    def test(self):
        args = Namespace(mine=False)
        self.make_response("machines.json")

        status = machines(args, self.gbp, self.console, self.errorf)

        self.assertEqual(status, 0)
        self.assertEqual(self.console.getvalue(), EXPECTED_OUTPUT)
        self.assert_graphql(queries.machines)

    def test_with_mine(self):
        args = Namespace(mine=True, my_machines="babette lighthouse")
        self.make_response("machines.json")

        status = machines(args, self.gbp, self.console, self.errorf)

        self.assertEqual(status, 0)
        expected = """\
           2 Machines           
╭────────────┬────────┬────────╮
│ Machine    │ Builds │ Latest │
├────────────┼────────┼────────┤
│ babette    │     14 │    631 │
│ lighthouse │     29 │  10694 │
╰────────────┴────────┴────────╯
"""
        self.assertEqual(self.console.getvalue(), expected)
        self.assert_graphql(queries.machines)


EXPECTED_OUTPUT = """\
           7 Machines           
╭────────────┬────────┬────────╮
│ Machine    │ Builds │ Latest │
├────────────┼────────┼────────┤
│ arm64-base │      6 │     36 │
│ babette    │     14 │    631 │
│ base       │     16 │    643 │
│ blackwidow │     24 │  10994 │
│ gbpbox     │     12 │    224 │
│ lighthouse │     29 │  10694 │
│ testing    │     23 │  10159 │
╰────────────┴────────┴────────╯
"""
