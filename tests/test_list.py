"""Tests for the list subcommand"""

# pylint: disable=missing-function-docstring,protected-access
from unittest import mock

from gbp_testkit.helpers import parse_args, print_command
from unittest_fixtures import Fixtures, given

from gbpcli.subcommands.list import handler as list_command

from . import LOCAL_TIMEZONE, TestCase, make_response


@given("gbp", "console")
@mock.patch("gbpcli.render.LOCAL_TIMEZONE", new=LOCAL_TIMEZONE)
class ListTestCase(TestCase):
    """list() tests"""

    def test(self, fixtures: Fixtures):
        cmdline = "gbp list jenkins"
        args = parse_args(cmdline)
        gbp = fixtures.gbp
        console = fixtures.console
        make_response(gbp, "list_with_packages.json")

        print_command(cmdline, console)
        status = list_command(args, gbp, console)

        self.assertEqual(status, 0)
        self.assertEqual(console.out.file.getvalue(), EXPECTED_OUTPUT)
        self.assert_graphql(
            gbp, gbp.query.gbpcli.builds, machine="jenkins", withPackages=True
        )


EXPECTED_OUTPUT = """$ gbp list jenkins
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
