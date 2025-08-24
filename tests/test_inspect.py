"""Tests for the inspect subcommand"""

# pylint: disable=missing-docstring
from typing import Sequence
from unittest import TestCase

import gbp_testkit.fixtures as testkit
from gbp_testkit.factories import package_factory
from gbp_testkit.helpers import LOCAL_TIMEZONE
from gentoo_build_publisher import publisher
from gentoo_build_publisher.types import Build
from unittest_fixtures import Fixtures, fixture, given, where


@fixture(testkit.publisher)
def inspect_fixture(
    _fixtures: Fixtures,
    machines: Sequence[str] = (),
    builds_per_machine: int = 1,
    packages_per_build: int = 2,
) -> None:
    pf = package_factory()
    builder = publisher.jenkins.artifact_builder  # type: ignore
    builder.timer = 1756068380
    build_id = 1

    for machine in machines:
        for _b in range(builds_per_machine):
            build = Build(machine=machine, build_id=str(build_id))
            for _p in range(packages_per_build):
                package = next(pf)
                builder.build(build, package)
            publisher.pull(build)
            build_id += 1
    publisher.save(publisher.record(build), note="Build note")


@given(inspect_fixture, testkit.gbpcli, testkit.environ, local_timezone=testkit.patch)
@where(inspect__machines=["base", "testing", "babette"])
@where(inspect__builds_per_machine=3)
@where(environ={"GBPCLI_MYMACHINES": "babette"})
@where(local_timezone__target="gbpcli.render.LOCAL_TIMEZONE")
@where(local_timezone__new=LOCAL_TIMEZONE)
class InspectTestCase(TestCase):
    """inspect() tests"""

    def test_entire_tree(self, fixtures: Fixtures):
        status = fixtures.gbpcli("gbp inspect")

        self.assertEqual(status, 0)
        self.assertEqual(fixtures.console.stdout, INSPECT_ALL)

    def test_single_machine(self, fixtures: Fixtures):
        status = fixtures.gbpcli("gbp inspect babette")

        self.assertEqual(status, 0)
        self.assertEqual(fixtures.console.stdout, INSPECT_SINGLE)

    def test_single_machine_with_tail(self, fixtures: Fixtures):
        status = fixtures.gbpcli("gbp inspect --tail=2 base")

        self.assertEqual(status, 0)
        self.assertEqual(fixtures.console.stdout, INSPECT_SINGLE_WITH_TAIL)

    def test_single_machine_with_build_id(self, fixtures: Fixtures):
        status = fixtures.gbpcli("gbp inspect base.2")

        self.assertEqual(status, 0, fixtures.console.stderr)
        self.assertEqual(fixtures.console.stdout, INSPECT_SINGLE_WITH_BUILD_ID)

    def test_with_mine(self, fixtures: Fixtures):
        status = fixtures.gbpcli("gbp inspect --mine")

        self.assertEqual(status, 0)
        self.assertEqual(fixtures.console.stdout, INSPECT_SINGLE_MINE)


INSPECT_SINGLE_WITH_TAIL = """$ gbp inspect --tail=2 base
Machines
└── base
    ├── 2 (08/24/25 13:46:50) 
    │   ├── dev-python/pycups-1.0 (13:47:00)
    │   └── dev-python/gcc-1.0 (13:47:10)
    └── 3 (08/24/25 13:47:20) 
        ├── dev-python/ffmpeg-1.0 (13:47:30)
        └── media-libs/markdown-1.0 (13:47:40)
"""
INSPECT_SINGLE = """$ gbp inspect babette
Machines
└── babette
    ├── 7 (08/24/25 13:49:20) 
    │   ├── app-admin/pycups-1.0 (13:49:30)
    │   └── app-admin/gcc-1.0 (13:49:40)
    ├── 8 (08/24/25 13:49:50) 
    │   ├── app-admin/ffmpeg-1.0 (13:50:00)
    │   └── net-im/markdown-1.0 (13:50:10)
    └── 9 (08/24/25 13:50:20) 
        ╭────────────╮        
        │ Build note │        
        ╰────────────╯        
        ├── net-im/mesa-1.0 (13:50:30)
        └── net-im/pycups-1.0 (13:50:40)
"""
INSPECT_SINGLE_MINE = """$ gbp inspect --mine
Machines
└── babette
    ├── 7 (08/24/25 13:49:20) 
    │   ├── app-admin/pycups-1.0 (13:49:30)
    │   └── app-admin/gcc-1.0 (13:49:40)
    ├── 8 (08/24/25 13:49:50) 
    │   ├── app-admin/ffmpeg-1.0 (13:50:00)
    │   └── net-im/markdown-1.0 (13:50:10)
    └── 9 (08/24/25 13:50:20) 
        ╭────────────╮        
        │ Build note │        
        ╰────────────╯        
        ├── net-im/mesa-1.0 (13:50:30)
        └── net-im/pycups-1.0 (13:50:40)
"""
INSPECT_ALL = """$ gbp inspect
Machines
├── babette
│   ├── 7 (08/24/25 13:49:20) 
│   │   ├── app-admin/pycups-1.0 (13:49:30)
│   │   └── app-admin/gcc-1.0 (13:49:40)
│   ├── 8 (08/24/25 13:49:50) 
│   │   ├── app-admin/ffmpeg-1.0 (13:50:00)
│   │   └── net-im/markdown-1.0 (13:50:10)
│   └── 9 (08/24/25 13:50:20) 
│       ╭────────────╮        
│       │ Build note │        
│       ╰────────────╯        
│       ├── net-im/mesa-1.0 (13:50:30)
│       └── net-im/pycups-1.0 (13:50:40)
├── base
│   ├── 1 (08/24/25 13:46:20) 
│   │   ├── dev-python/markdown-1.0 (13:46:30)
│   │   └── dev-python/mesa-1.0 (13:46:40)
│   ├── 2 (08/24/25 13:46:50) 
│   │   ├── dev-python/pycups-1.0 (13:47:00)
│   │   └── dev-python/gcc-1.0 (13:47:10)
│   └── 3 (08/24/25 13:47:20) 
│       ├── dev-python/ffmpeg-1.0 (13:47:30)
│       └── media-libs/markdown-1.0 (13:47:40)
└── testing
    ├── 4 (08/24/25 13:47:50) 
    │   ├── media-libs/mesa-1.0 (13:48:00)
    │   └── media-libs/pycups-1.0 (13:48:10)
    ├── 5 (08/24/25 13:48:20) 
    │   ├── media-libs/gcc-1.0 (13:48:30)
    │   └── media-libs/ffmpeg-1.0 (13:48:40)
    └── 6 (08/24/25 13:48:50) 
        ├── app-admin/markdown-1.0 (13:49:00)
        └── app-admin/mesa-1.0 (13:49:10)
"""
INSPECT_SINGLE_WITH_BUILD_ID = """$ gbp inspect base.2
Machines
└── base
    └── 2 (08/24/25 13:46:50) 
        ├── dev-python/pycups-1.0 (13:47:00)
        └── dev-python/gcc-1.0 (13:47:10)
"""
