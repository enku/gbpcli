"""Tests for the GBP interface"""

# pylint: disable=missing-docstring,protected-access
import os

import requests.exceptions
from unittest_fixtures import depends, requires

from gbpcli import GBP, build_parser, config

from . import TestCase, make_response


@requires("gbp")
class GGPTestCase(TestCase):
    def test_search_notes_deprecation(self):
        gbp = self.fixtures.gbp
        make_response(gbp, "search_notes.json")

        with self.assertWarns(DeprecationWarning) as context:
            gbp.search_notes("lighthouse", "test")

        self.assertEqual(
            context.warning.args[0], "This method is deprecated. Use search() instead"
        )

    def test_url(self) -> None:
        gbp = GBP("http://gbp.invalid/")

        self.assertEqual(gbp.query._url, "http://gbp.invalid/graphql")


@requires("gbp")
class GBPQueryTestCase(TestCase):
    """Tests for the .query method"""

    def test_does_not_exit_when_flag_turned_off(self):
        gbp = self.fixtures.gbp
        gbp.exit_gracefully_on_requests_errors = False
        error = requests.exceptions.ConnectionError()
        gbp.query._session.post.side_effect = error

        with self.assertRaises(requests.exceptions.ConnectionError) as cxt:
            gbp.query.gbpcli.machines()

        self.assertIs(cxt.exception, error)


@depends("environ")
def parser(_options, _fixtures):
    return build_parser(config.Config())


@requires("tempdir", parser)
class BuildParserTestCase(TestCase):
    """Tests for the build_parser method"""

    def test_my_machines_string(self):
        argv = ["--my-machines", "this that the other"]

        args = self.fixtures.parser.parse_args(argv)

        self.assertEqual(args.my_machines, "this that the other")

    def test_my_machines_not_passed(self):
        argv = []

        args = self.fixtures.parser.parse_args(argv)

        self.assertEqual(args.my_machines, "")

    def test_my_machines_from_environ(self):
        os.environ["GBPCLI_MYMACHINES"] = "this that the other"
        argv = []

        parser_ = build_parser(config.Config())
        args = parser_.parse_args(argv)

        self.assertEqual(args.my_machines, "this that the other")
