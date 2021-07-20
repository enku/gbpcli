"""Tests for the Gentoo Build Publisher CLI"""
import datetime
from json import dumps as stringify
from pathlib import Path
from unittest import mock

import requests

DATA_DIR = Path(__file__).resolve().parent / "data"
LOCAL_TIMEZONE = datetime.timezone(datetime.timedelta(days=-1, seconds=61200), "PDT")
NO_JSON = object()


def load_data(filename: str) -> bytes:
    """Read and return content from filename in the data directory"""
    return (DATA_DIR / filename).read_bytes()


def make_response(status_code=200, json=NO_JSON, content=None) -> mock.Mock:
    """Create a mock requests.Response object"""
    if content is None:
        content = b"test"
        text = "test"
    else:
        text = None

    attrs = {
        "content": content,
        "headers": {},
        "status_code": status_code,
        "text": text,
    }

    if json is not NO_JSON:
        attrs["json.return_value"] = json
        attrs["content"] = stringify(json, sort_keys=True).encode("utf-8")
        attrs["headers"] = {"content-type": "application/json"}

    response_mock = mock.Mock(spec=requests.Response)
    response_mock.configure_mock(**attrs)

    return response_mock
