import datetime
import time


def get_unix_time():

    return  int( (time.mktime(datetime.datetime.now().timetuple())) )
