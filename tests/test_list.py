"""Tests for the list subcommand"""

# pylint: disable=missing-docstring
import datetime as dt
from unittest import TestCase

import gbp_testkit.fixtures as testkit
from gbp_testkit.helpers import LOCAL_TIMEZONE
from gentoo_build_publisher import publisher
from gentoo_build_publisher.records import BuildRecord
from gentoo_build_publisher.types import Build
from unittest_fixtures import Fixtures, fixture, given, where

from . import lib

DEFAULT_DELTA = dt.timedelta(minutes=10)
DEFAULT_START_DATE = dt.datetime(2025, 8, 23, tzinfo=dt.UTC)


@fixture(testkit.publisher)
def builds_fixture(
    _: Fixtures,
    machine: str = "jenkins",
    count: int = 4,
    stop: int = 36,
    start_date: dt.datetime = DEFAULT_START_DATE,
    delta: dt.timedelta = DEFAULT_DELTA,
) -> list[BuildRecord]:
    lib.create_machine_builds(machine, count, stop)

    records: list[BuildRecord] = []
    built = start_date
    for build in reversed(list(publisher.repo.build_records.for_machine(machine))):
        records.append(publisher.save(build, built=built))
        built += delta

    return records


@given(testkit.gbpcli, builds_fixture, final=lib.pulled_build)
@where(final__build=Build(machine="jenkins", build_id="37"))
@where(final__packages=["dev-libs/nss-3.115.1"])
@where(final__built=dt.datetime(2025, 8, 24, tzinfo=dt.UTC))
@given(local_timezone=testkit.patch)
@where(local_timezone__target="gbpcli.render.LOCAL_TIMEZONE")
@where(local_timezone__new=LOCAL_TIMEZONE)
class ListTestCase(TestCase):
    """list() tests"""

    def test(self, fixtures: Fixtures):
        builds = fixtures.builds
        publisher.save(builds[0], keep=True)
        publisher.save(builds[2], note="This is a test")
        final = fixtures.final
        publisher.save(final, note="This is a test")
        publisher.publish(final)
        publisher.tag(final, "hello")
        publisher.tag(final, "world")

        status = fixtures.gbpcli("gbp list jenkins")

        self.assertEqual(status, 0)
        self.assertEqual(fixtures.console.stdout, EXPECTED_OUTPUT)


EXPECTED_OUTPUT = """$ gbp list jenkins
                    💻 jenkins                    
╭───────┬────┬───────────────────┬───────────────╮
│ Flags │ ID │ Built             │ Tags          │
├───────┼────┼───────────────────┼───────────────┤
│  K    │ 33 │ 08/22/25 17:00:00 │               │
│       │ 34 │ 08/22/25 17:10:00 │               │
│    N  │ 35 │ 08/22/25 17:20:00 │               │
│       │ 36 │ 08/22/25 17:30:00 │               │
│ * PN  │ 37 │ 08/23/25 17:00:00 │ @hello @world │
╰───────┴────┴───────────────────┴───────────────╯
"""
