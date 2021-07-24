"""Utility functions"""
import datetime
from typing import Literal, Optional

from gbpcli import LOCAL_TIMEZONE

JSON_CONTENT_TYPE = "application/json"


def timestr(
    timestamp: datetime.datetime, timezone: Optional[datetime.tzinfo] = None
) -> str:
    """Humanize JSON timestamp string"""
    timezone = timezone or LOCAL_TIMEZONE
    dt_obj = timestamp.astimezone(timezone)

    return dt_obj.strftime("%c %z")


def yesno(value: bool) -> Literal["yes", "no"]:
    """Convert bool value to 'yes' or 'no'"""
    if value:
        return "yes"

    return "no"
