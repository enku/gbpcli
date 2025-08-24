"""Tests for the machines subcommand"""

# pylint: disable=missing-docstring
from unittest import TestCase

import gbp_testkit.fixtures as testkit
from unittest_fixtures import Fixtures, fixture, given, where

from . import lib


@fixture(testkit.publisher)
def builds_fixture(_: Fixtures) -> None:
    lib.create_machine_builds("arm64-base", 1, 36)
    lib.create_machine_builds("babette", 2, 631)
    lib.create_machine_builds("base", 3, 643)
    lib.create_machine_builds("blackwidow", 4, 10994)
    lib.create_machine_builds("gbpbox", 5, 224)
    lib.create_machine_builds("lighthouse", 6, 10694)
    lib.create_machine_builds("testing", 7, 10159)


@given(builds_fixture)
@given(testkit.gbpcli, testkit.environ)
@where(environ={"GBPCLI_MYMACHINES": "babette lighthouse"})
class MachinesTestCase(TestCase):
    """machines() tests"""

    def test(self, fixtures: Fixtures):
        status = fixtures.gbpcli("gbp machines")

        self.assertEqual(status, 0)
        self.assertEqual(fixtures.console.stdout, EXPECTED_OUTPUT)

    def test_with_mine(self, fixtures: Fixtures):
        status = fixtures.gbpcli("gbp machines --mine")

        self.assertEqual(status, 0)
        expected = """$ gbp machines --mine
           2 Machines           
╭────────────┬────────┬────────╮
│ Machine    │ Builds │ Latest │
├────────────┼────────┼────────┤
│ babette    │      2 │    631 │
│ lighthouse │      6 │  10694 │
╰────────────┴────────┴────────╯
"""
        self.assertEqual(fixtures.console.stdout, expected)


EXPECTED_OUTPUT = """$ gbp machines
           7 Machines           
╭────────────┬────────┬────────╮
│ Machine    │ Builds │ Latest │
├────────────┼────────┼────────┤
│ arm64-base │      1 │     36 │
│ babette    │      2 │    631 │
│ base       │      3 │    643 │
│ blackwidow │      4 │  10994 │
│ gbpbox     │      5 │    224 │
│ lighthouse │      6 │  10694 │
│ testing    │      7 │  10159 │
╰────────────┴────────┴────────╯
"""
