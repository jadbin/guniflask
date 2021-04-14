from pydantic.datetime_parse import parse_datetime


def convert_to_datetime(s):
    return parse_datetime(s).astimezone()
