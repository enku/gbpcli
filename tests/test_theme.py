"""Tests for the theme module"""

# pylint: disable=missing-docstring
from typing import Any
from unittest import TestCase

from rich.theme import Theme

from gbpcli.theme import DEFAULT_THEME, get_theme_from_string


class GetColormapFromString(TestCase):
    """Tests for the get_theme_from_string function"""

    default_theme = get_theme_from_string(
        ":".join(f"{key}={value}" for key, value in DEFAULT_THEME.items())
    )

    def test_empty_string(self):
        theme = get_theme_from_string("")

        self.assert_themes_are_equal(theme, self.default_theme)

    def test_double_colons(self):
        string = "header=blue:note=bold::build_id=#889721"
        #                              ^^
        theme = get_theme_from_string(string)

        self.assert_theme_color(theme, "header", "blue")
        self.assertTrue(theme.styles["note"].bold)
        self.assert_theme_color(theme, "build_id", "#889721")

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

        self.assert_themes_are_equal(theme, self.default_theme)

    def test_garbage_input(self):
        with self.assertRaises(ValueError) as context:
            get_theme_from_string("This is totally garbage!")

        self.assertEqual(
            str(context.exception),
            "Invalid theme assignment: 'This is totally garbage!'",
        )

    def assert_themes_are_equal(self, first: Theme, second: Theme, msg: Any = None):
        """Compare two rich themes"""
        self.assertEqual(first.styles, second.styles, msg)

    def assert_theme_color(self, theme: Theme, style: str, color: str, msg: Any = None):
        """Assert the theme's style is the given color"""
        style_color = theme.styles[style].color
        assert style_color is not None, msg
        self.assertEqual(style_color.name, color, msg)
