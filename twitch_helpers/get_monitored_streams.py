
from typing import List

from twitchAPI import Twitch

from Database.live_twitch_instance import LiveTwitchInstance
from Database.monitor import get_all_monitors, get_all_logins
from cloud_logger import cloud_logger
from config.db_config import db


def get_monitored_streams(twitch_api: Twitch ):
    cloud_logger()
    user_logins = get_all_logins( )
    if len(user_logins) == 0:
        return []
    live_streams = twitch_api.get_streams(user_login=user_logins)
    if live_streams and 'data' in live_streams:
        return list(map(lambda x: LiveTwitchInstance(x), live_streams['data']))
    print("live streams didn't return a valid response")
    return []

def get_monitored_streams_dicts(twitch_api: Twitch ):
    cloud_logger()
    user_logins = get_all_logins( )
    if len(user_logins) == 0:
        return []
    live_streams = twitch_api.get_streams(user_login=user_logins)
    if live_streams and 'data' in live_streams:
        return live_streams['data']
    print("live streams didn't return a valid response")
    return []




def filterTheDict(dictObj, callback):

    newDict = dict()
    # Iterate over all the items in dictionary
    for (key, value) in dictObj.items():
        # Check if item satisfies the given condition then add to new dict
        if callback((key, value)):
            newDict[key] = value
    return newDict