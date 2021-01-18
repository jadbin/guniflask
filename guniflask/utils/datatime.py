import datetime as dt


def convert_to_datetime(s):
    if isinstance(s, int) or (isinstance(s, str) and s.isdigit()):
        return dt.datetime.fromtimestamp(int(s), tz=dt.timezone.utc).astimezone()
    if isinstance(s, str):
        if 'GMT' in s:
            return dt.datetime.strptime(s, '%a, %d %b %Y %H:%M:%S GMT').replace(tzinfo=dt.timezone.utc).astimezone()
    return s
