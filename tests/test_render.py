# pylint: disable=missing-docstring
import argparse
import datetime as dt
from unittest import TestCase

from gbpcli.render import format_machine, format_tags, timestr, yesno


class YesNoTestCase(TestCase):
    """Tests for the yesno() function"""

    def test_true(self):
        self.assertEqual("yes", yesno(True))

    def test_false(self):
        self.assertEqual("no", yesno(False))


class TimestrTestCase(TestCase):
    """timestr() tests"""

    def test(self):
        timestamp = dt.datetime.fromisoformat("2021-07-20T16:45:06.445500+00:00")
        timezone = dt.timezone(dt.timedelta(days=-1, seconds=61200), "PDT")

        self.assertEqual(timestr(timestamp, timezone), "Tue Jul 20 09:45:06 2021 -0700")


class FormatTagsTest(TestCase):
    """Tests for the format_tags method"""

    def test_single_tag(self):
        tag_str = format_tags(["first"])

        self.assertEqual(tag_str, "[tag]@first[/tag]")

    def test_no_tags(self):
        tag_str = format_tags([])

        self.assertEqual(tag_str, "")

    def test_multiple_tags(self):
        tag_str = format_tags(["this", "that", "the", "other"])

        self.assertEqual(tag_str, "[tag]@this @that @the @other[/tag]")

    def test_published_tag(self):
        tag_str = format_tags(["", "first"])

        self.assertEqual(tag_str, "[tag]@first[/tag]")


class FormatMachineTest(TestCase):
    """Test for the format_machines method"""

    def test_when_machine_is_mymachine(self):
        machine = "polaris"
        args = argparse.Namespace(my_machines="polaris")

        formatted = format_machine(machine, args)

        expected = "[machine][mymachine]polaris[/mymachine][/machine]"
        self.assertEqual(formatted, expected)

    def test_when_machine_is_not_mymachine(self):
        machine = "polaris"
        args = argparse.Namespace(my_machines="lighthouse babette")

        formatted = format_machine(machine, args)

        expected = "[machine]polaris[/machine]"
        self.assertEqual(formatted, expected)
