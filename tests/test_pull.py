"""Tests for the pull subcommand"""

# pylint: disable=missing-function-docstring,protected-access
from unittest import mock

from unittest_fixtures import requires

from gbpcli.subcommands.pull import handler as pull

from . import LOCAL_TIMEZONE, TestCase, make_response, parse_args


@requires("gbp", "console")
@mock.patch("gbpcli.render.LOCAL_TIMEZONE", new=LOCAL_TIMEZONE)
class PullTestCase(TestCase):
    """pull() tests"""

    def test(self):
        cmdline = "gbp pull lighthouse 3226"
        args = parse_args(cmdline)
        gbp = self.fixtures.gbp
        console = self.fixtures.console
        make_response(gbp, "pull.json")

        pull(args, gbp, console)

        self.assert_graphql(
            gbp, gbp.query.gbpcli.pull, id="lighthouse.3226", note=None, tags=None
        )

    def test_with_note(self) -> None:
        cmdline = "gbp pull lighthouse 3226 --note='This is a test'"
        args = parse_args(cmdline)
        gbp = self.fixtures.gbp
        console = self.fixtures.console
        make_response(gbp, "pull.json")

        pull(args, gbp, console)

        self.assert_graphql(
            gbp,
            gbp.query.gbpcli.pull,
            id="lighthouse.3226",
            note="This is a test",
            tags=None,
        )

    def test_with_tags(self) -> None:
        cmdline = "gbp pull lighthouse 3226 --tag test"
        args = parse_args(cmdline)
        gbp = self.fixtures.gbp
        console = self.fixtures.console
        make_response(gbp, "pull.json")

        pull(args, gbp, console)

        self.assert_graphql(
            gbp, gbp.query.gbpcli.pull, id="lighthouse.3226", note=None, tags=["test"]
        )
