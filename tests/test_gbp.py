"""Tests for the GBP interface"""

# pylint: disable=missing-docstring,protected-access,unused-argument
import os
from unittest import TestCase

import gbp_testkit.fixtures as testkit
import requests.exceptions
from unittest_fixtures import Fixtures, fixture, given, where

from gbpcli import build_parser, config
from gbpcli.gbp import GBP


class GGPTestCase(TestCase):
    def test_url(self) -> None:
        gbp = GBP("http://gbp.invalid/")

        self.assertEqual(gbp.query._url, "http://gbp.invalid/graphql")


@given(post=testkit.patch)
@where(post__target="requests.Session.post")
class GBPQueryTestCase(TestCase):
    """Tests for the .query method"""

    def test_does_not_exit_when_flag_turned_off(self, fixtures: Fixtures):
        gbp = GBP("http://gbp.invalid/")
        error = requests.exceptions.ConnectionError()
        fixtures.post.side_effect = error

        with self.assertRaises(requests.exceptions.ConnectionError) as cxt:
            gbp.query.gbpcli.machines()  # type: ignore[attr-defined]

        self.assertIs(cxt.exception, error)


@fixture(testkit.environ)
def parser(_fixtures):
    return build_parser(config.Config())


@given(testkit.tmpdir, parser)
class BuildParserTestCase(TestCase):
    """Tests for the build_parser method"""

    def test_my_machines_string(self, fixtures: Fixtures):
        argv = ["--my-machines", "this that the other"]

        args = fixtures.parser.parse_args(argv)

        self.assertEqual(args.my_machines, "this that the other")

    def test_my_machines_not_passed(self, fixtures: Fixtures):
        argv: list[str] = []

        args = fixtures.parser.parse_args(argv)

        self.assertEqual(args.my_machines, "")

    def test_my_machines_from_environ(self, fixtures: Fixtures):
        os.environ["GBPCLI_MYMACHINES"] = "this that the other"
        argv: list[str] = []

        parser_ = build_parser(config.Config())
        args = parser_.parse_args(argv)

        self.assertEqual(args.my_machines, "this that the other")
