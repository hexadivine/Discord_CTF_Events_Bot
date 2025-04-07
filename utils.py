from datetime import datetime, timedelta
import time

def str_to_timestamp(utc_time_str):
    utc_time = datetime.fromisoformat(utc_time_str)
    # sydney_offset = timedelta(hours=11)
    # sydney_time = utc_time + sydney_offset
    unix_timestamp = int(utc_time.timestamp())
    return unix_timestamp

def utc_to_syd_time(utc_time_str):
    utc_time = datetime.fromisoformat(utc_time_str)
    sydney_offset = timedelta(hours=11)
    sydney_time = utc_time + sydney_offset
    # unix_timestamp = int(utc_time.timestamp())
    return sydney_time


def format_timestamp(iso_str):
    dt = datetime.fromisoformat(iso_str.replace("Z", "+00:00"))
    return f"<t:{int(dt.timestamp())}:F>"