"""Utility functions"""
import datetime
from typing import Literal, Optional

import requests

from gbpcli import LOCAL_TIMEZONE, APIError, NotFound, UnexpectedResponseError

JSON_CONTENT_TYPE = "application/json"


def check(response: requests.Response, is_json: bool = True):
    """Check the requests response.

    If the status code 404, raise NotFound
    """
    if response.status_code == 404:
        raise NotFound

    if is_json:
        if (
            response.headers.get("content-type", "").partition(";")[0]
            != JSON_CONTENT_TYPE
        ):
            raise UnexpectedResponseError(response)

        data = response.json()

        if error := data["error"]:
            raise APIError(error, data)

        return data

    return response.content


def timestr(timestamp: str, timezone: Optional[datetime.tzinfo] = None) -> str:
    """Humanize JSON timestamp string"""
    timezone = timezone or LOCAL_TIMEZONE
    dt_obj = datetime.datetime.fromisoformat(timestamp).astimezone(timezone)

    return dt_obj.strftime("%c %z")


def yesno(value: bool) -> Literal["yes", "no"]:
    """Convert bool value to 'yes' or 'no'"""
    if value:
        return "yes"

    return "no"
