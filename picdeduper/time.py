from datetime import datetime, timezone

Timestamp = float
TimeString = str

def datetime_for_string(time_string: TimeString) -> datetime:
    return datetime.strptime(time_string, "%Y-%m-%d %H:%M:%S %z")

def timestamp_for_string(time_string: TimeString) -> Timestamp:
    return datetime_for_string(time_string).timestamp()

def datetime_for_timestamp(timestamp: Timestamp) -> datetime:
    return datetime.utcfromtimestamp(timestamp)
    
def string_for_timestamp(timestamp: Timestamp) -> TimeString:
    """Always returns in UTC"""
    return datetime_for_timestamp(timestamp).strftime("%Y-%m-%d %H:%M:%S +0000")

def time_strings_are_same_time(a: TimeString, b: TimeString):
    if a == b: 
        return True
    return timestamp_for_string(a) == timestamp_for_string(b)
