"""Tests for the theme module"""
# pylint: disable=missing-docstring


from gbpcli.theme import DEFAULT_THEME, get_theme_from_string

from . import ThemeTests


class GetColormapFromString(ThemeTests):
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
