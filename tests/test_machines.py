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
