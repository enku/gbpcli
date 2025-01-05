"""Show the GBP builds as a tree"""

import argparse
import datetime as dt

from rich.console import RenderableType
from rich.panel import Panel
from rich.table import Table
from rich.tree import Tree

from gbpcli import GBP, render, utils
from gbpcli.subcommands import completers as comp
from gbpcli.types import Build, Console, Package

HELP = """Show the GBP builds as a tree

Display all the builds (or the last n builds if --tail is given) for all the
machines (or only the machines given).  Display the build's timestamp as well as
the timestamp for each build's packages' completion.  If the build has a note
that will be displayed as well.
"""


def handler(args: argparse.Namespace, gbp: GBP, console: Console) -> int:
    """Show the machines builds as a tree"""
    tree = Tree("[header]Machines[/header]", guide_style="box")

    for machine in get_machines(args, gbp):
        if "." in machine:
            try:
                machine, build = get_dotted_machine_and_build(machine, gbp)
                builds = [build]
            except utils.ResolveBuildError:
                console.err.print("Not found")
                return 1
        else:
            builds = gbp.builds(machine, with_packages=True)[-1 * args.tail :]

        branch = tree.add(render.format_machine(machine, args))

        for build in builds:
            assert build.info

            p_branch = branch.add(render_build(build))
            build_date = (
                (build.info.built or build.info.submitted)
                .astimezone(render.LOCAL_TIMEZONE)
                .date()
            )
            packages: list[Package] = build.packages_built or []
            packages = sort_packages_by_build_time(packages)

            for package in packages:
                p_branch.add(render_package(package, build_date))

    console.out.print(tree)

    return 0


def get_machines(args: argparse.Namespace, gbp: GBP) -> list[str]:
    """Return the list of machines requested by the arguments

    - If --mine is passed then use --my-machines is returned
    - If machine[s] are passed on the command-line they are returned
    - Otherwise returns the list of all machines on the server
    """
    if args.mine:
        return utils.get_my_machines_from_args(args)

    machine: list[str] = args.machine
    if machine:
        return machine

    return gbp.machine_names()


def sort_packages_by_build_time(packages: list[Package]) -> list[Package]:
    """Missing docstring"""
    sorted_packages = [*packages]
    sorted_packages.sort(key=lambda p: getattr(p, "build_time", dt.datetime.min))

    return sorted_packages


def render_build(build: Build) -> RenderableType:
    """Convert `build` into a rich renderable"""
    assert build.info

    build_str = f"[build_id]{build.number}[/build_id]"

    if build.info.published:
        build_str = f"[published]{build_str}[/published]"

    timestamp = (build.info.built or build.info.submitted).astimezone(
        render.LOCAL_TIMEZONE
    )
    build_str = f"{build_str} [timestamp]({timestamp.strftime('%x %X')})[/timestamp]"

    tag_strs = (
        [f"[tag]@{tag}[/tag]" for tag in build.info.tags] if build.info.tags else []
    )

    build_str = f"{build_str} {' '.join(tag_strs)}"

    if note := build.info.note:
        note = note.rstrip("\n")
        grid = Table.grid()
        grid.add_column()
        grid.add_row(build_str)
        grid.add_row(Panel(f"[note]{note}[/note]", expand=False, style="box"))

        return grid

    return build_str


def render_package(package: Package, build_build_date: dt.date) -> str:
    """Convert `package` into a rich renderable"""
    local_build_time = package.build_time.astimezone(render.LOCAL_TIMEZONE)
    build_time = (
        local_build_time.strftime("%x %X")
        if local_build_time.date() != build_build_date
        else str(local_build_time.time())
    )

    return f"[package]{package.cpv}[/package] [timestamp]({build_time})[/timestamp]"


def get_dotted_machine_and_build(machine_dot_build: str, gbp: GBP) -> tuple[str, Build]:
    """Split machine_dot_build and return the machine name and Build"""
    machine, _, number = machine_dot_build.partition(".")
    build = gbp.get_build_info(Build(machine=machine, number=int(number)))

    if build is None:
        raise utils.ResolveBuildError(machine_dot_build)

    return machine, build


def parse_args(parser: argparse.ArgumentParser) -> None:
    """Set subcommand arguments"""
    parser.add_argument("-t", "--tail", type=int, default=0)
    parser.add_argument("--mine", action="store_true", default=False)
    comp.set(parser.add_argument("machine", nargs="*"), comp.machines)
