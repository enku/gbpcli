"""gbpcli configuration

This module adds helpers for reading an gbpcli configuration from a file. This can be
used instead of or in addition to the command-line arguments.
"""

import typing as t
from dataclasses import dataclass

try:
    import tomllib
except ImportError:  # pragma: no cover
    import toml as tomlib  # pylint: disable=unused-import


SECTION = "gbpcli"


class AuthDict(t.TypedDict):
    """User authorization pair"""

    user: str
    api_key: str


_T = t.TypeVar("_T", bound="Config")


@dataclass(kw_only=True, frozen=True, slots=True)
class Config:
    """gbpcli config file structure"""

    url: str | None = None
    my_machines: list[str] | None = None
    auth: AuthDict | None = None

    @classmethod
    def from_file(cls: type[_T], fp: t.IO[bytes]) -> _T:
        """Return a Config instance given the config file"""
        toml_data = tomllib.load(fp)
        gbpcli_data = get_section(toml_data, SECTION)

        return cls(**gbpcli_data)


def get_section(toml_data: dict[str, t.Any], section: str) -> dict[str, t.Any]:
    """Return the given section from the toml_data dict

    If the given section does not exist, raise ConfigError
    """
    try:
        return toml_data[section]
    except KeyError as error:
        raise ConfigError(f"Missing section: {section}") from error


class ConfigError(Exception):
    """Config errors"""
