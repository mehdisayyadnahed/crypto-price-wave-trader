"""
This module handles date and time extractions. It provides utility functions 
to retrieve time segments (year, month, day, hour, minute, second) 
or Unix epoch timestamps according to a specified timezone (default is Asia/Tehran).
"""

from datetime import datetime
import time

# Handle zoneinfo import fallback for older Python versions (Python < 3.9)
try:
    from zoneinfo import ZoneInfo
except ImportError:
    from backports.zoneinfo import ZoneInfo


def date_time_func(mode, target_location="Asia/Tehran"):
    """
    Returns specific time elements or formatted timestamps based on the requested mode.
    Supported modes: "all", "year", "month", "day", "hour", "minute", "second", "epoch".
    """
    tz = ZoneInfo(target_location)

    if mode == "all":
        return str(datetime.now(tz).strftime("%Y-%m-%d %H:%M:%S"))
    if mode == "year":
        return str(datetime.now(tz).strftime("%Y"))
    if mode == "month":
        return str(datetime.now(tz).strftime("%m"))
    if mode == "day":
        return str(datetime.now(tz).strftime("%d"))
    if mode == "hour":
        return str(datetime.now(tz).strftime("%H"))
    if mode == "minute":
        return str(datetime.now(tz).strftime("%M"))
    if mode == "second":
        return str(datetime.now(tz).strftime("%S"))
    if mode == "epoch":
        return int(time.time())


# =====================================================================
# Developer Testing Examples (Kept intact for configuration reference)
# =====================================================================
# print(date_time_func("all", "Asia/Tehran"))
# print(int(time.time()) + 60)