from datetime import datetime


def get_unix_time():
    presentDate = datetime.now()
    unix_timestamp = datetime.timestamp(presentDate) * 1000
    return unix_timestamp
