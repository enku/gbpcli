"""Tests for the theme module"""
# pylint: disable=missing-docstring
from unittest import TestCase

from gbpcli.theme import DEFAULT_THEME, get_theme_from_string


class GetColormapFromString(TestCase):
    """Tests for the get_theme_from_string function"""

    def test_empty_string(self):
        theme = get_theme_from_string("")
        default = get_theme_from_string(
            ":".join(f"{key}={value}" for key, value in DEFAULT_THEME.items())
        )
        self.assertEqual(theme.styles, default.styles)

    def test_double_colons(self):
        string = "header=blue:note=bold::build_id=#889721"
        #                             ^^
        theme = get_theme_from_string(string)

        self.assertEqual(theme.styles["header"].color.name, "blue")
        self.assertTrue(theme.styles["note"].bold)
        self.assertEqual(theme.styles["build_id"].color.name, "#889721")

    def test_double_equals(self):
        string = "header=blue:notes==white:build_id=bold"
        #                          ^^

        with self.assertRaises(ValueError) as context:
            get_theme_from_string(string)

        self.assertEqual(
            str(context.exception), "Invalid theme assignment: 'notes==white'"
        )

    def test_missing_equals(self):
        string = "header=test_header:note:build_id=test_build_id"
        #                                ^

        with self.assertRaises(ValueError) as context:
            get_theme_from_string(string)

        self.assertEqual(str(context.exception), "Invalid theme assignment: 'note'")

    def test_only_colons(self):
        theme = get_theme_from_string("::::::::::")
        default = get_theme_from_string(
            ":".join(f"{key}={value}" for key, value in DEFAULT_THEME.items())
        )

        self.assertEqual(theme.styles, default.styles)

    def test_garbage_input(self):
        with self.assertRaises(ValueError) as context:
            get_theme_from_string("This is totally garbage!")

        self.assertEqual(
            str(context.exception),
            "Invalid theme assignment: 'This is totally garbage!'",
        )
