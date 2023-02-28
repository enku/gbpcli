"""Tests for the GBP interface"""
# pylint: disable=missing-docstring,protected-access
import os
from unittest import mock

import requests.exceptions

from gbpcli import DEFAULT_THEME, build_parser, get_colormap_from_string

from . import TestCase


class GBPQueryTestCase(TestCase):
    """Tests for the .query method"""

    def test_does_not_exit_when_flag_turned_off(self):
        self.gbp.exit_gracefully_on_requests_errors = False
        error = requests.exceptions.ConnectionError()
        self.gbp.query._session.post.side_effect = error

        with self.assertRaises(requests.exceptions.ConnectionError) as cxt:
            self.gbp.query.machines()

        self.assertIs(cxt.exception, error)


class GetColormapFromString(TestCase):
    """Tests for the get_colormap_from_string function"""

    def test_empty_string(self):
        result = get_colormap_from_string("")

        self.assertEqual(result, DEFAULT_THEME)

    def test_double_colons(self):
        string = "header=test_header:note=test_note::build_id=test_build_id"
        #                                          ^^
        result = get_colormap_from_string(string)

        self.assertEqual(result["header"], "test_header")
        self.assertEqual(result["note"], "test_note")
        self.assertEqual(result["build_id"], "test_build_id")

    def test_double_equals(self):
        string = "header=blue:notes==white:build_id=bold"
        #                          ^^

        with self.assertRaises(ValueError) as context:
            get_colormap_from_string(string)

        self.assertEqual(
            str(context.exception),
            "Invalid color map: 'header=blue:notes==white:build_id=bold'",
        )

    def test_missing_equals(self):
        string = "header=test_header:note:build_id=test_build_id"
        #                                ^

        with self.assertRaises(ValueError) as context:
            get_colormap_from_string(string)

        self.assertEqual(
            str(context.exception),
            "Invalid color map: 'header=test_header:note:build_id=test_build_id'",
        )

    def test_only_colons(self):
        result = get_colormap_from_string("::::::::::")

        self.assertEqual(result, DEFAULT_THEME)

    def test_garbage_input(self):
        with self.assertRaises(ValueError) as context:
            get_colormap_from_string("This is totally garbage!")

        self.assertEqual(
            str(context.exception),
            "Invalid color map: 'This is totally garbage!'",
        )

    def test_ignores_unknown_names(self):
        string = "header=test_header:note=test_note:unknown=test_unknown"

        result = get_colormap_from_string(string)

        self.assertEqual(result["header"], "test_header")
        self.assertEqual(result["note"], "test_note")
        self.assertFalse("unknown" in result)


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
