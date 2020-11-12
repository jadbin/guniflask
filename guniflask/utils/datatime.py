import datetime as dt


def convert_to_datetime(s):
    if isinstance(s, int):
        return dt.datetime.fromtimestamp(s, tz=dt.timezone.utc).astimezone()
    elif isinstance(s, str):
        if 'GMT' in s:
            return dt.datetime.strptime(s, '%a, %d %b %Y %H:%M:%S GMT').replace(tzinfo=dt.timezone.utc).astimezone()
    return s
