"""Tests for the machines subcommand"""

# pylint: disable=missing-function-docstring,protected-access,unused-argument
import gbp_testkit.fixtures as testkit
from gentoo_build_publisher import publisher
from gentoo_build_publisher.types import Build
from unittest_fixtures import Fixtures, fixture, given, where

from . import lib


@fixture(testkit.publisher)
def builds_fixture(_: Fixtures) -> None:
    create_machine_builds("arm64-base", 6, 36)
    create_machine_builds("babette", 14, 631)
    create_machine_builds("base", 16, 643)
    create_machine_builds("blackwidow", 24, 10994)
    create_machine_builds("gbpbox", 12, 224)
    create_machine_builds("lighthouse", 29, 10694)
    create_machine_builds("testing", 23, 10159)


@given(builds_fixture)
@given(testkit.gbpcli, testkit.environ, lib.local_timezone)
@where(environ={"GBPCLI_MYMACHINES": "babette lighthouse"})
class MachinesTestCase(lib.TestCase):
    """machines() tests"""

    def test(self, fixtures: Fixtures):
        status = fixtures.gbpcli("gbp machines")

        self.assertEqual(status, 0)
        self.assertEqual(fixtures.console.out.file.getvalue(), EXPECTED_OUTPUT)

    def test_with_mine(self, fixtures: Fixtures):
        status = fixtures.gbpcli("gbp machines --mine")

        self.assertEqual(status, 0)
        expected = """$ gbp machines --mine
           2 Machines           
╭────────────┬────────┬────────╮
│ Machine    │ Builds │ Latest │
├────────────┼────────┼────────┤
│ babette    │     14 │    631 │
│ lighthouse │     29 │  10694 │
╰────────────┴────────┴────────╯
"""
        self.assertEqual(fixtures.console.out.file.getvalue(), expected)


def create_machine_builds(machine: str, count: int, stop: int):
    for i in range(stop - count + 1, stop + 1):
        publisher.pull(Build(machine=machine, build_id=str(i)))


EXPECTED_OUTPUT = """$ gbp machines
           7 Machines           
╭────────────┬────────┬────────╮
│ Machine    │ Builds │ Latest │
├────────────┼────────┼────────┤
│ arm64-base │      6 │     36 │
│ babette    │     14 │    631 │
│ base       │     16 │    643 │
│ blackwidow │     24 │  10994 │
│ gbpbox     │     12 │    224 │
│ lighthouse │     29 │  10694 │
│ testing    │     23 │  10159 │
╰────────────┴────────┴────────╯
"""
