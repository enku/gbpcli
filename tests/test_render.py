# pylint: disable=missing-docstring,unused-argument
import argparse
import datetime as dt
from unittest import TestCase

import gbp_testkit.fixtures as testkit
from gbp_testkit.helpers import LOCAL_TIMEZONE
from unittest_fixtures import Fixtures, given, where

from gbpcli.render import (
    build_to_str,
    format_flags,
    format_machine,
    format_tags,
    timestr,
    yesno,
)
from gbpcli.types import Build, BuildInfo, Package


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


@given(local_timezone=testkit.patch)
@where(local_timezone__target="gbpcli.render.LOCAL_TIMEZONE")
@where(local_timezone__new=LOCAL_TIMEZONE)
class BuildToStrTests(TestCase):
    build = Build(
        machine="babette",
        number=12,
        info=BuildInfo(
            keep=False,
            note="This is a test",
            published=True,
            tags=["@foo", "@bar"],
            submitted=dt.datetime(2025, 4, 8, 7, 1, tzinfo=dt.UTC),
            built=dt.datetime(2025, 4, 8, 6, 1, tzinfo=dt.UTC),
            completed=dt.datetime(2025, 4, 8, 7, 10, tzinfo=dt.UTC),
        ),
        packages_built=[
            Package(
                cpv="app-arch/libarchive-3.7.9",
                build_time=dt.datetime(2025, 4, 8, 6, 10, tzinfo=dt.UTC),
            ),
            Package(
                cpv="sys-apps/acl-2.3.2-r2",
                build_time=dt.datetime(2025, 4, 8, 6, 20, tzinfo=dt.UTC),
            ),
        ],
    )

    def test(self, fixtures: Fixtures) -> None:
        result = build_to_str(self.build)

        expected = """\
[bold]Build:[/bold] [blue]babette/12[/blue]
[bold]BuildDate:[/bold] Mon Apr  7 23:01:00 2025 -0700
[bold]Submitted:[/bold] Tue Apr  8 00:01:00 2025 -0700
[bold]Completed:[/bold] Tue Apr  8 00:10:00 2025 -0700
[bold]Published:[/bold] yes
[bold]Keep:[/bold] no
[bold]Tags:[/bold] @foo @bar
[bold]Packages-built:[/bold]
    app-arch/libarchive-3.7.9
    sys-apps/acl-2.3.2-r2

This is a test

"""
        self.assertEqual(expected, result)

    def test_no_info(self, fixtures: Fixtures) -> None:
        build = Build(machine="babette", number=12)

        with self.assertRaises(ValueError):
            build_to_str(build)


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


class FormatFlagsTests(TestCase):
    """Tests for the format_flags method"""

    def test(self) -> None:
        build = Build(
            machine="babette",
            number=123,
            info=BuildInfo(
                keep=False,
                note=None,
                published=True,
                tags=["foo"],
                submitted=dt.datetime(2025, 6, 13, 6, 50, tzinfo=dt.UTC),
                completed=dt.datetime(2025, 6, 13, 6, 55, tzinfo=dt.UTC),
                built=dt.datetime(2025, 6, 13, 6, 49, tzinfo=dt.UTC),
            ),
            packages_built=[
                Package(
                    cpv="media-video/totem-43.2",
                    build_time=dt.datetime(2025, 6, 13, 4, 49, tzinfo=dt.UTC),
                )
            ],
        )
        self.assertEqual(
            "[package]*[/package] [published]P[/published] ", format_flags(build)
        )

    def test_build_without_info(self) -> None:
        build = Build(
            machine="babette",
            number=123,
            info=None,
            packages_built=[
                Package(
                    cpv="media-video/totem-43.2",
                    build_time=dt.datetime(2025, 6, 13, 4, 49, tzinfo=dt.UTC),
                )
            ],
        )
        with self.assertRaises(ValueError):
            format_flags(build)
