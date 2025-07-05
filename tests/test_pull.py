"""Tests for the pull subcommand"""

# pylint: disable=missing-function-docstring,protected-access
import gbp_testkit.fixtures as testkit
from gbp_testkit.helpers import parse_args
from unittest_fixtures import Fixtures, given

from gbpcli.subcommands.pull import handler as pull

from . import lib


@given(lib.gbp, testkit.console, lib.local_timezone)
class PullTestCase(lib.TestCase):
    """pull() tests"""

    def test(self, fixtures: Fixtures):
        cmdline = "gbp pull lighthouse 3226"
        args = parse_args(cmdline)
        gbp = fixtures.gbp
        console = fixtures.console
        lib.make_response(gbp, "pull.json")

        pull(args, gbp, console)

        self.assert_graphql(
            gbp, gbp.query.gbpcli.pull, id="lighthouse.3226", note=None, tags=None
        )

    def test_with_note(self, fixtures: Fixtures) -> None:
        cmdline = "gbp pull lighthouse 3226 --note='This is a test'"
        args = parse_args(cmdline)
        gbp = fixtures.gbp
        console = fixtures.console
        lib.make_response(gbp, "pull.json")

        pull(args, gbp, console)

        self.assert_graphql(
            gbp,
            gbp.query.gbpcli.pull,
            id="lighthouse.3226",
            note="This is a test",
            tags=None,
        )

    def test_with_tags(self, fixtures: Fixtures) -> None:
        cmdline = "gbp pull lighthouse 3226 --tag test"
        args = parse_args(cmdline)
        gbp = fixtures.gbp
        console = fixtures.console
        lib.make_response(gbp, "pull.json")

        pull(args, gbp, console)

        self.assert_graphql(
            gbp, gbp.query.gbpcli.pull, id="lighthouse.3226", note=None, tags=["test"]
        )
