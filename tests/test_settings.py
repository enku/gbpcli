"""Tests for GBP Settings"""

# pylint: disable=missing-docstring,unused-argument
import datetime as dt
import os
from dataclasses import dataclass
from pathlib import Path
from typing import ClassVar
from unittest import TestCase

import gbp_testkit.fixtures as testkit
from unittest_fixtures import Fixtures, given, where

from gbpcli.settings import BaseSettings, string_value_to_field_value

svtfv = string_value_to_field_value


@dataclass(kw_only=True, frozen=True)
class Settings(BaseSettings):
    env_prefix: ClassVar = "BUILD_PUBLISHER_"

    # pylint: disable=invalid-name
    STORAGE_PATH: Path
    FLAG: bool
    JENKINS_DOWNLOAD_CHUNK_SIZE: int
    JENKINS_USER: str | None = None
    TIMESTAMP: dt.datetime = dt.datetime(2025, 9, 14, 14, 1)

    @staticmethod
    def validate_timestamp(value: str) -> dt.datetime:
        return dt.datetime.fromisoformat(value)


@given(testkit.environ)
@where(environ__clear=True)
class SettingsTestCase(TestCase):
    def test_from_environ(self, fixtures: Fixtures) -> None:
        data_dict = {
            "BUILD_PUBLISHER_JENKINS_USER": "fail",
            "TODAY_IS": "your birthday",
            "TODAY_JENKINS_BASE_URL": "https://jenkins.invalid/",
            "TODAY_JENKINS_DOWNLOAD_CHUNK_SIZE": "14",
            "TODAY_FLAG": "no",
            "TODAY_STORAGE_PATH": "/home/today",
        }
        os.environ.update(data_dict)

        settings = Settings.from_environ(prefix="TODAY_")

        self.assertEqual(settings.STORAGE_PATH, Path("/home/today"))
        self.assertEqual(settings.JENKINS_USER, None)
        self.assertEqual(settings.JENKINS_DOWNLOAD_CHUNK_SIZE, 14)
        self.assertIs(settings.FLAG, False)

    def test_from_dict(self, fixtures: Fixtures) -> None:
        data_dict = {
            "BUILD_PUBLISHER_JENKINS_USER": "fail",
            "TODAY_IS": "your birthday",
            "TODAY_JENKINS_BASE_URL": "https://jenkins.invalid/",
            "TODAY_JENKINS_DOWNLOAD_CHUNK_SIZE": "14",
            "TODAY_STORAGE_PATH": "/home/today",
            "TODAY_FLAG": "yes",
            "TODAY_TIMESTAMP": "2002-11-04 04:15:22",
        }
        prefix = "TODAY_"

        settings = Settings.from_dict(prefix, data_dict)

        self.assertEqual(settings.STORAGE_PATH, Path("/home/today"))
        self.assertEqual(settings.JENKINS_USER, None)
        self.assertEqual(settings.JENKINS_DOWNLOAD_CHUNK_SIZE, 14)
        self.assertIs(settings.FLAG, True)
        self.assertEqual(settings.TIMESTAMP, dt.datetime(2002, 11, 4, 4, 15, 22))

        with self.assertRaises(AttributeError):
            # pylint: disable=no-member,pointless-statement
            settings.IS  # type: ignore


class StringValueToFieldValue(TestCase):
    def test_int(self) -> None:
        self.assertEqual(58, svtfv("58", int))

    def test_int_str(self) -> None:
        self.assertEqual(58, svtfv("58", "int"))

    def test_bool_str(self) -> None:
        self.assertEqual(True, svtfv("True", "bool"))
        self.assertEqual(False, svtfv("False", "bool"))
        self.assertEqual(False, svtfv("No", "bool"))

    def test_path(self) -> None:
        self.assertEqual(Path("/dev/null"), svtfv("/dev/null", Path))

    def test_path_str(self) -> None:
        self.assertEqual(Path("/dev/null"), svtfv("/dev/null", "Path"))

    def test_other(self) -> None:
        self.assertEqual("None", svtfv("None", type(None)))
