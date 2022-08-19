import datetime
import tempfile
import time


def get_unix_time():
    return int((time.mktime(datetime.datetime.now().timetuple())))


def temp_name():
    return next(tempfile._get_candidate_names())
