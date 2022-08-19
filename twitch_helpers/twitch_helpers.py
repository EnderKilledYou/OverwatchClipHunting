import sys

from twitchAPI import Twitch, AuthScope

from cloud_logger import cloud_error_logger
from config.config import consumer_key, consumer_secret, access_token, refresh_token

user_id = None
twitch_api = None


def get_twitch_api():
    global twitch_api
    try:
        if twitch_api is not None:
            return twitch_api
        twitch = Twitch(app_id=consumer_key, app_secret=consumer_secret)
        twitch.auto_refresh_auth = True
        twitch.set_user_authentication(access_token, [AuthScope.CLIPS_EDIT], refresh_token, validate=False)
        twitch.refresh_used_token()

        # print(me)
        twitch_api = twitch
    except BaseException as e:
        cloud_error_logger(e)
        return None
    return twitch


def get_broadcaster_id(broadcaster: str):
    twitch = get_twitch_api()
    try:
        user = twitch.get_users(logins=[broadcaster])["data"][0]

        return user['id']
    except BaseException as e:
        print(
            "Looks like that broad caster doesn't exist or your refresh token is bad. Try it again with a different token")
        sys.exit(1)
