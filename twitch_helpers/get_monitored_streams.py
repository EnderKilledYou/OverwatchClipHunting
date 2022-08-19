from typing import List

from twitchAPI import Twitch

from Database.live_twitch_instance import LiveTwitchInstance
from cloud_logger import cloud_logger


def get_monitored_streams(twitch_api: Twitch, user_logins: List[str]):
    cloud_logger()
    if len(user_logins) == 0:
        return []
    live_streams = twitch_api.get_streams(user_login=user_logins)
    if live_streams and 'data' in live_streams:

        return list(map(lambda x: LiveTwitchInstance().from_web(x), live_streams['data']))
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