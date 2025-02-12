"""Tests for the machines subcommand"""

# pylint: disable=missing-function-docstring,protected-access
from unittest import mock

from unittest_fixtures import requires

from gbpcli.subcommands.machines import handler as machines

from . import LOCAL_TIMEZONE, TestCase, make_response, parse_args, print_command


@requires("gbp", "console", "environ")
@mock.patch("gbpcli.render.LOCAL_TIMEZONE", new=LOCAL_TIMEZONE)
class MachinesTestCase(TestCase):
    """machines() tests"""

    options = {"environ": {"GBPCLI_MYMACHINES": "babette lighthouse"}}

    def test(self):
        cmdline = "gbp machines"
        args = parse_args(cmdline)
        gbp = self.fixtures.gbp
        console = self.fixtures.console
        make_response(gbp, "machines.json")

        print_command(cmdline, console)
        status = machines(args, gbp, console)

        self.assertEqual(status, 0)
        self.assertEqual(console.out.file.getvalue(), EXPECTED_OUTPUT)
        self.assert_graphql(gbp, gbp.query.gbpcli.machines, names=None)

    def test_with_mine(self):
        cmdline = "gbp machines --mine"
        args = parse_args(cmdline)
        gbp = self.fixtures.gbp
        console = self.fixtures.console
        make_response(gbp, "machines_filtered.json")

        print_command(cmdline, console)
        status = machines(args, gbp, console)

        self.assertEqual(status, 0)
        expected = """$ gbp machines --mine
           2 Machines           
╭────────────┬────────┬────────╮
│ Machine    │ Builds │ Latest │
├────────────┼────────┼────────┤
│ babette    │     14 │    631 │
│ lighthouse │     29 │  10694 │
╰────────────┴────────┴────────╯
"""
        self.assertEqual(console.out.file.getvalue(), expected)
        self.assert_graphql(
            gbp, gbp.query.gbpcli.machines, names=["babette", "lighthouse"]
        )


EXPECTED_OUTPUT = """$ gbp machines
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
