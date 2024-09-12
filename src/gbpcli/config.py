"""gbpcli configuration

This module adds helpers for reading an gbpcli configuration from a file. This can be
used instead of or in addition to the command-line arguments.
"""

import os
import platform
import stat
import sys
import tomllib
import typing as t
from dataclasses import dataclass

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

        config = cls(**gbpcli_data)

        if config.auth:
            maybe_warn_on_perms(fp.fileno())

        return config


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


def maybe_warn_on_perms(fp: int | str) -> None:
    """Check if the file is readable by others and if so write a warning to stderr"""
    if is_readable_by_others(fp):
        sys.stderr.write(
            "Warning: the config file contains secrets yet is readable by others.\n"
        )


def is_readable_by_others(fp: int | str) -> bool:
    """Return True if the given file can be read by a user other than the owner"""
    if platform.system() in ["Unix", "Linux", "Darwin"]:
        st_mode = os.stat(fp).st_mode
        group_readable = bool(st_mode & stat.S_IRGRP)
        others_readable = bool(st_mode & stat.S_IROTH)

        return group_readable or others_readable

    raise NotImplementedError(
        "File permission checks for this platform are not supported"
    )
