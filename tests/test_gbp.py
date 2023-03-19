"""Tests for the GBP interface"""
# pylint: disable=missing-docstring,protected-access
import os
from unittest import mock

import requests.exceptions

from gbpcli import build_parser

from . import TestCase


class GGPTestCase(TestCase):
    def test_search_notes_deprecation(self):
        self.make_response("search_notes.json")

        with self.assertWarns(DeprecationWarning) as context:
            self.gbp.search_notes("lighthouse", "test")

        self.assertEqual(
            context.warning.args[0], "This method is deprecated. Use search() instead"
        )


class GBPQueryTestCase(TestCase):
    """Tests for the .query method"""

    def test_does_not_exit_when_flag_turned_off(self):
        self.gbp.exit_gracefully_on_requests_errors = False
        error = requests.exceptions.ConnectionError()
        self.gbp.query._session.post.side_effect = error

        with self.assertRaises(requests.exceptions.ConnectionError) as cxt:
            self.gbp.query.machines()

        self.assertIs(cxt.exception, error)


class BuildParserTestCase(TestCase):
    """Tests for the build_parser method"""

    def setUp(self):
        super().setUp()

        patch = mock.patch.dict(os.environ, clear=True)
        self.addCleanup(patch.stop)
        patch.start()

    def test_my_machines_string(self):
        argv = ["--my-machines", "this that the other"]

        parser = build_parser()
        args = parser.parse_args(argv)

        self.assertEqual(args.my_machines, "this that the other")

    def test_my_machines_not_passed(self):
        argv = []

        parser = build_parser()
        args = parser.parse_args(argv)

        self.assertEqual(args.my_machines, "")

    def test_my_machines_from_environ(self):
        os.environ["GBPCLI_MYMACHINES"] = "this that the other"
        argv = []

        parser = build_parser()
        args = parser.parse_args(argv)

        self.assertEqual(args.my_machines, "this that the other")
