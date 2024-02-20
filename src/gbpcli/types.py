"""gbp-cli data types"""

import datetime as dt
from dataclasses import dataclass
from enum import Enum, IntEnum
from typing import Any, TypeVar

import rich.console


@dataclass(frozen=True, kw_only=True, slots=True)
class BuildInfo:
    """Metadata about a Build

    Retrieved from the API.
    """

    keep: bool
    note: str | None
    published: bool
    tags: list[str]
    submitted: dt.datetime
    completed: dt.datetime | None = None
    built: dt.datetime | None = None


@dataclass(frozen=True, kw_only=True, slots=True)
class Package:
    """A (binary) package"""

    cpv: str
    build_time: dt.datetime


T = TypeVar("T", bound="Build")


@dataclass(frozen=True, kw_only=True, slots=True)
class Build:
    """A GBP Build"""

    machine: str
    number: int
    info: BuildInfo | None = None
    packages_built: list[Package] | None = None

    @property
    def id(self) -> str:  # pylint: disable=invalid-name
        """Return the GBP build id"""
        return f"{self.machine}.{self.number}"

    @classmethod
    def from_id(cls: type[T], build_id: str, **kwargs: Any) -> T:
        """Create from GBP build id"""
        parts = build_id.partition(".")

        return cls(machine=parts[0], number=int(parts[2]), **kwargs)

    @classmethod
    def from_api_response(cls: type[T], api_response: dict[str, Any]) -> T:
        """Return a Build with BuildInfo given the response from the API"""
        completed = api_response.get("completed")
        submitted = api_response["submitted"]
        fromisoformat = dt.datetime.fromisoformat
        built = api_response.get("built")

        packages_built = (
            None
            if (packages := api_response.get("packagesBuilt", None)) is None
            else [
                Package(
                    cpv=i["cpv"],
                    build_time=dt.datetime.fromtimestamp(i.get("buildTime", 0)),
                )
                for i in packages
            ]
        )

        return cls.from_id(
            api_response["id"],
            info=BuildInfo(
                keep=api_response.get("keep", False),
                published=api_response.get("published", False),
                tags=api_response.get("tags", []),
                note=api_response.get("notes"),
                submitted=fromisoformat(submitted),
                completed=fromisoformat(completed) if completed is not None else None,
                built=fromisoformat(built) if built is not None else None,
            ),
            packages_built=packages_built,
        )


class ChangeState(IntEnum):
    """Diff status"""

    REMOVED = -1
    CHANGED = 0
    ADDED = 1


class SearchField(Enum):
    """Search fields"""

    # pylint: disable=invalid-name

    logs = "LOGS"
    notes = "NOTES"


@dataclass(frozen=True, kw_only=True, slots=True)
class Change:
    """Item in a diff"""

    item: str
    status: ChangeState


@dataclass(frozen=True, kw_only=True, slots=True)
class Console:
    """Output sinks for handlers"""

    out: rich.console.Console
    err: rich.console.Console
