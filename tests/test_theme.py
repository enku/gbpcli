"""Tests for the theme module"""
# pylint: disable=missing-docstring
from unittest import TestCase

from gbpcli.theme import DEFAULT_THEME, get_colormap_from_string


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
