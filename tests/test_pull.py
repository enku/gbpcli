"""Tests for the pull subcommand"""

# pylint: disable=missing-function-docstring,protected-access
from argparse import Namespace
from unittest import mock

from unittest_fixtures import requires

from gbpcli.subcommands.pull import handler as pull

from . import LOCAL_TIMEZONE, TestCase, make_response


@requires("gbp", "console")
@mock.patch("gbpcli.render.LOCAL_TIMEZONE", new=LOCAL_TIMEZONE)
class PullTestCase(TestCase):
    """pull() tests"""

    def test(self):
        args = Namespace(machine="lighthouse", number="3226", note=None, tags=None)
        gbp = self.fixtures.gbp
        console = self.fixtures.console
        make_response(gbp, "pull.json")

        pull(args, gbp, console)

        self.assert_graphql(
            gbp, gbp.query.gbpcli.pull, id="lighthouse.3226", note=None, tags=None
        )

    def test_with_note(self) -> None:
        args = Namespace(
            machine="lighthouse", number="3226", note="This is a test", tags=None
        )
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
        tags = ["this", "is", "a", "test"]
        args = Namespace(machine="lighthouse", number="3226", note=None, tags=tags)
        gbp = self.fixtures.gbp
        console = self.fixtures.console
        make_response(gbp, "pull.json")

        pull(args, gbp, console)

        self.assert_graphql(
            gbp, gbp.query.gbpcli.pull, id="lighthouse.3226", note=None, tags=tags
        )
