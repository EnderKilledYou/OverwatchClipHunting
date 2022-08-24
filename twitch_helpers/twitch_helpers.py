
import sys

from twitchAPI import Twitch, AuthScope

from Database.Twitch.twitch_response import TwitchResponse, get_response_by_twitch_id
from cloud_logger import cloud_error_logger
from config.config import consumer_key, consumer_secret, access_token, refresh_token

user_id = None
twitch_api = None


class InvalidTwitchUserError:
    pass


def get_twitch_api(user: str=None):
    twitch = Twitch(app_id=consumer_key, app_secret=consumer_secret)
    twitch.auto_refresh_auth = True
    twitch.set_user_authentication(access_token, [AuthScope.CLIPS_EDIT], refresh_token,validate=False)
    twitch.refresh_used_token()
    return twitch
    resp = get_response_by_twitch_id(user)
    if resp is None:
        raise InvalidTwitchUserError(user)
    return get_twitch_api_with_resp(resp)


def get_twitch_api_with_resp(resp: TwitchResponse):
    global twitch_api
    try:

        twitch = Twitch(app_id=consumer_key, app_secret=consumer_secret)
        twitch.auto_refresh_auth = True
        twitch.set_user_authentication(resp.access_token, [AuthScope.CLIPS_EDIT], resp.refresh_token, validate=False)
        twitch.refresh_used_token()

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
