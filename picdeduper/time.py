from datetime import datetime

Timestamp = float
TimeString = str


def datetime_from_string(time_string: TimeString) -> datetime:
    if not time_string: return None
    return datetime.strptime(time_string, "%Y-%m-%d %H:%M:%S %z")


def timestamp_from_string(time_string: TimeString) -> Timestamp:
    if not time_string: return None
    return datetime_from_string(time_string).timestamp()


def datetime_from_timestamp(timestamp: Timestamp) -> datetime:
    if not timestamp: return None
    return datetime.utcfromtimestamp(timestamp)


def string_from_timestamp(timestamp: Timestamp) -> TimeString:
    """Always returns in UTC"""
    if not timestamp: return None
    return datetime_from_timestamp(timestamp).strftime("%Y-%m-%d %H:%M:%S +0000")


def time_strings_are_same_time(a: TimeString, b: TimeString):
    if a == b:
        return True
    return timestamp_from_string(a) == timestamp_from_string(b)

def seconds_between_times(a: Timestamp, b: Timestamp):
    """Params a & b can be either our Timestamp or Python's datetime or time strings"""
    if not a or not b:
        return None
    if isinstance(a, datetime):
        a = a.timestamp()
    if isinstance(a, str):
        a = timestamp_from_string(a)
    if isinstance(b, datetime):
        b = b.timestamp()
    if isinstance(b, str):
        b = timestamp_from_string(b)
    return abs(a - b)