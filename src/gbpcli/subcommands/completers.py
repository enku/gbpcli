"""argcomplete completers"""
# pylint: disable=unused-argument
import argparse
from typing import Iterable, Protocol

from gbpcli import GBP


class Completer(Protocol):  # pylint: disable=too-few-public-methods
    """Completer function"""

    def __call__(
        self,
        *,
        prefix: str,
        action: argparse.Action,
        parser: argparse.ArgumentParser,
        parsed_args: argparse.Namespace,
    ) -> Iterable[str]:
        ...


def machines(
    *,
    prefix: str,
    action: argparse.Action,
    parser: argparse.ArgumentParser,
    parsed_args: argparse.Namespace,
) -> list[str]:
    """Completer for machine names"""
    gbp = GBP(parsed_args.url)
    gbp_machines = (i[0] for i in gbp.machines())

    return [machine for machine in gbp_machines if machine.startswith(prefix)]


def build_ids(
    *,
    prefix: str,
    action: argparse.Action,
    parser: argparse.ArgumentParser,
    parsed_args: argparse.Namespace,
) -> list[str]:
    """Completer for build IDs (numbers)"""
    machine = parsed_args.machine
    gbp = GBP(parsed_args.url)
    numbers = (str(build.number) for build in gbp.builds(machine))

    return [number for number in numbers if number.startswith(prefix)]


def set(  # pylint: disable=redefined-builtin
    action: argparse.Action, completer: Completer
) -> None:
    """Set the completer for the given action"""
    setattr(action, "completer", completer)
