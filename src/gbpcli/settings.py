"""From gbpcli"""

import os
from dataclasses import dataclass, fields
from pathlib import Path
from typing import Any, ClassVar, Self

from strtobool import strtobool  # type: ignore


@dataclass(kw_only=True, frozen=True)
class BaseSettings:
    """Base class for Settings

    Subclasses should define me as the prefix for environment variables for these
    settings. For example if prefix is "BUILD_PUBLISHER_" and the field is named "FOO"
    then the environment variable for that field is "BUILD_PUBLISHER_FOO"
    """

    env_prefix: ClassVar = ""

    @classmethod
    def from_dict(cls: type[Self], prefix: str, data_dict: dict[str, Any]) -> Self:
        """Return Settings instantiated from a dict"""
        params: dict[str, Any] = {}

        for field in fields(cls):
            if (key := f"{prefix}{field.name}") not in data_dict:
                continue

            value = string_value_to_field_value(data_dict[key], field.type)

            if validator := getattr(cls, f"validate_{field.name.lower()}", None):
                value = validator(value)  # pylint: disable=not-callable

            params[field.name] = value

        return cls(**params)

    @classmethod
    def from_environ(cls: type[Self], prefix: str | None = None) -> Self:
        """Return settings instantiated from environment variables"""
        prefix = prefix if prefix is not None else cls.env_prefix

        return cls.from_dict(prefix, dict(os.environ))


def string_value_to_field_value(value: str, type_: str | type[Any]) -> Any:
    """Coerse the given string value to the given type"""
    match getattr(type_, "__name__", type_):
        case "bool":
            return get_bool(value)
        case "int":
            return int(value)
        case "Path":
            return Path(value)
        case _:
            return value


def get_bool(value: str | bytes | bool) -> bool:
    """Return the boolean value of the truthy/falsey string"""
    if isinstance(value, bool):
        return value

    if isinstance(value, bytes):
        value = value.decode("UTF-8")

    return bool(strtobool(value))
