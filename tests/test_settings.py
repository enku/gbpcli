"""Tests for GBP Settings"""

# pylint: disable=missing-class-docstring,missing-function-docstring
from dataclasses import dataclass
from pathlib import Path
from typing import ClassVar
from unittest import TestCase, mock

from gbpcli.settings import BaseSettings


@dataclass(kw_only=True, frozen=True)
class Settings(BaseSettings):
    env_prefix: ClassVar = "BUILD_PUBLISHER_"

    # pylint: disable=invalid-name
    STORAGE_PATH: Path
    FLAG: bool
    JENKINS_DOWNLOAD_CHUNK_SIZE: int
    JENKINS_USER: str | None = None


class SettingsTestCase(TestCase):
    def test_from_environ(self) -> None:
        data_dict = {
            "BUILD_PUBLISHER_JENKINS_USER": "fail",
            "TODAY_IS": "your birthday",
            "TODAY_JENKINS_BASE_URL": "https://jenkins.invalid/",
            "TODAY_JENKINS_DOWNLOAD_CHUNK_SIZE": "14",
            "TODAY_FLAG": "no",
            "TODAY_STORAGE_PATH": "/home/today",
        }

        with mock.patch.dict("gbpcli.settings.os.environ", data_dict, clear=True):
            settings = Settings.from_environ(prefix="TODAY_")

        self.assertEqual(settings.STORAGE_PATH, Path("/home/today"))
        self.assertEqual(settings.JENKINS_USER, None)
        self.assertEqual(settings.JENKINS_DOWNLOAD_CHUNK_SIZE, 14)
        self.assertIs(settings.FLAG, False)

    def test_from_dict(self) -> None:
        data_dict = {
            "BUILD_PUBLISHER_JENKINS_USER": "fail",
            "TODAY_IS": "your birthday",
            "TODAY_JENKINS_BASE_URL": "https://jenkins.invalid/",
            "TODAY_JENKINS_DOWNLOAD_CHUNK_SIZE": "14",
            "TODAY_STORAGE_PATH": "/home/today",
            "TODAY_FLAG": "yes",
        }
        prefix = "TODAY_"

        settings = Settings.from_dict(prefix, data_dict)

        self.assertEqual(settings.STORAGE_PATH, Path("/home/today"))
        self.assertEqual(settings.JENKINS_USER, None)
        self.assertEqual(settings.JENKINS_DOWNLOAD_CHUNK_SIZE, 14)
        self.assertIs(settings.FLAG, True)

        with self.assertRaises(AttributeError):
            # pylint: disable=no-member,pointless-statement
            settings.IS  # type: ignore
