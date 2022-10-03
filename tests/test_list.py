"""Tests for the list subcommand"""
# pylint: disable=missing-function-docstring
from argparse import Namespace
from unittest import mock

from gbpcli import queries
from gbpcli.subcommands.list import handler as list_command

from . import LOCAL_TIMEZONE, TestCase, mock_print


@mock.patch("gbpcli.subcommands.list.LOCAL_TIMEZONE", new=LOCAL_TIMEZONE)
class ListTestCase(TestCase):
    """list() tests"""

    maxDiff = None

    @mock_print("gbpcli.subcommands.list")
    def test(self, _print_mock):
        args = Namespace(machine="jenkins")
        self.make_response("list_with_packages.json")

        status = list_command(args, self.gbp, self.console)

        self.assertEqual(status, 0)
        self.assertEqual(self.console.getvalue(), EXPECTED_OUTPUT)
        self.assert_graphql(queries.builds_with_packages, machine="jenkins")


EXPECTED_OUTPUT = """\
                    💻 jenkins                    
╭───────┬────┬───────────────────┬───────────────╮
│ Flags │ ID │ Built             │ Tags          │
├───────┼────┼───────────────────┼───────────────┤
│  K    │  1 │ 04/25/21 21:47:27 │               │
│       │ 12 │ 04/26/21 13:24:42 │               │
│       │ 18 │ 05/26/21 14:22:50 │               │
│    N  │ 23 │ 06/27/21 07:26:41 │               │
│    N  │ 28 │ 07/21/21 18:28:16 │               │
│    N  │ 37 │ 08/31/21 13:42:23 │               │
│    N  │ 41 │ 09/28/21 14:18:42 │               │
│    N  │ 50 │ 10/26/21 14:55:29 │               │
│ *  N  │ 51 │ 11/02/21 15:21:00 │               │
│ * PN  │ 52 │ 11/09/21 14:51:08 │ @hello @world │
╰───────┴────┴───────────────────┴───────────────╯
"""
