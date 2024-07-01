from datetime import datetime, timedelta
from functools import lru_cache

import pytz


def parsed_timezones():
    today = datetime.now().date()
    return _timezones(today)


@lru_cache
def _timezones(_: datetime):
    timezones = []
    for timezone_name in pytz.common_timezones:
        now = datetime.now(pytz.timezone(timezone_name))

        timezones.append({
            'name': timezone_name,
            'parsed_offset': parse_offset(now.utcoffset())
        })
    return timezones


def parse_offset(delta: timedelta):
    sign = '+' if delta.days >= 0 else '-'
    minutes = abs((delta.days * 24 * 60 * 60) + delta.seconds) // 60
    hours = minutes // 60
    minutes = minutes % 60
    return f'{sign}{hours:02d}:{minutes:02d}'


def previous_minute_multiple(date: datetime, minute_multiple: int):
    previous_multiple = (date.minute // minute_multiple) * minute_multiple
    return date.replace(minute=previous_multiple, second=0, microsecond=0)


def previous_hour_multiple(date: datetime, hour_multiple: int):
    previous_multiple = (date.hour // hour_multiple) * hour_multiple
    return date.replace(hour=previous_multiple, minute=0, second=0, microsecond=0)
