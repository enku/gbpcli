"""Tests for the show subcommand"""
# pylint: disable=missing-function-docstring
from argparse import Namespace
from unittest import mock

from gbpcli import queries
from gbpcli.subcommands.show import handler as show

from . import LOCAL_TIMEZONE, TestCase, mock_print


@mock.patch("gbpcli.utils.LOCAL_TIMEZONE", new=LOCAL_TIMEZONE)
@mock_print("gbpcli.subcommands.show")
class ShowTestCase(TestCase):
    """show() tests"""

    maxDiff = None

    def test(self, print_mock):
        args = Namespace(machine="lighthouse", number=2080)
        self.make_response("show.json")

        show(args, self.gbp)

        expected = """\
Build: lighthouse/3109
Submitted: Sat Oct  2 07:26:19 2021 -0700
Completed: Sat Oct  2 07:41:25 2021 -0700
Published: yes
Keep: no

    Packages built:
    
    * app-text/poppler-21.10.0-1
    * dev-perl/URI-5.90.0-1
    * net-im/signal-desktop-bin-5.18.0-1
    * net-print/cups-filters-1.28.10-3
"""
        self.assertEqual(print_mock.stdout.getvalue(), expected)
        self.assert_graphql(queries.build, name="lighthouse", number=2080)

    def test_should_get_latest_when_number_is_none(self, _print_mock):
        args = Namespace(machine="lighthouse", number=None)
        self.make_response({"data": {"latest": {"number": 2080}}})
        self.make_response("show.json")

        status = show(args, self.gbp)

        self.assert_graphql(queries.latest, index=0, name="lighthouse")
        self.assert_graphql(queries.build, index=1, name="lighthouse", number=2080)
        self.assertEqual(status, 0)

    def test_should_print_error_when_build_does_not_exist(self, print_mock):
        args = Namespace(machine="bogus", number=934)
        self.make_response({"data": {"build": None}})

        status = show(args, self.gbp)

        self.assertEqual(status, 1)
        self.assertEqual(print_mock.stderr.getvalue(), "Build not found\n")
