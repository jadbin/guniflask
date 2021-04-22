import datetime as dt

from pydantic.datetime_parse import parse_datetime

local_tz_info = dt.datetime.now().astimezone().tzinfo


def convert_to_datetime(s):
    return parse_datetime(s).astimezone()
