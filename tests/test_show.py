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
        args = Namespace(machine="lighthouse", number=3587)
        self.make_response("show.json")

        show(args, self.gbp)

        expected = """\
Build: lighthouse/3587
Submitted: Fri Nov 12 21:25:53 2021 -0700
Completed: Fri Nov 12 21:29:34 2021 -0700
Published: no
Keep: no
Packages-built:
\tapp-editors/vim-8.2.3582
\tapp-editors/vim-core-8.2.3582

"""
        self.assertEqual(print_mock.stdout.getvalue(), expected)
        self.assert_graphql(queries.build, id="lighthouse.3587")

    def test_should_get_latest_when_number_is_none(self, _print_mock):
        args = Namespace(machine="lighthouse", number=None)
        self.make_response({"data": {"latest": {"id": "lighthouse.3587"}}})
        self.make_response("show.json")

        status = show(args, self.gbp)

        self.assert_graphql(queries.latest, index=0, name="lighthouse")
        self.assert_graphql(queries.build, index=1, id="lighthouse.3587")
        self.assertEqual(status, 0)

    def test_should_print_error_when_build_does_not_exist(self, print_mock):
        args = Namespace(machine="bogus", number=934)
        self.make_response({"data": {"build": None}})

        status = show(args, self.gbp)

        self.assertEqual(status, 1)
        self.assertEqual(print_mock.stderr.getvalue(), "Build not found\n")
