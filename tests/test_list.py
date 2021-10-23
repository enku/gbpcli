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
    def test(self, print_mock):
        args = Namespace(machine="jenkins")
        self.make_response("list.json")

        status = list_command(args, self.gbp)

        self.assertEqual(status, 0)
        self.assertEqual(print_mock.stdout.getvalue(), EXPECTED_OUTPUT)
        self.assert_graphql(queries.builds, name="jenkins")


EXPECTED_OUTPUT = """\
[K  ]     1 04/25/21 21:47:27
[   ]    12 04/26/21 13:24:42
[   ]    18 05/26/21 14:22:50
[  N]    23 06/27/21 07:26:41
[  N]    28 07/21/21 18:28:16
[  N]    37 08/31/21 13:42:23
[ PN]    38 09/07/21 14:07:00
[  N]    41 09/28/21 14:18:42
[  N]    42 10/02/21 09:10:41
"""
