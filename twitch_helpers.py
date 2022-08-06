import sys

from twitchAPI import Twitch, AuthScope

from config.config import consumer_key, consumer_secret, access_token, refresh_token, broadcaster


def get_twitch_api():
    try:
        twitch = Twitch(app_id=consumer_key, app_secret=consumer_secret)
        twitch.auto_refresh_auth = True
        twitch.set_user_authentication(access_token, [AuthScope.CLIPS_EDIT], refresh_token)
        twitch.refresh_used_token()
    except BaseException as e:
        print(
            "Your token is bad. Try it again with a different token")
        sys.exit(1)
    return twitch


def get_broadcaster_id():
    twitch = get_twitch_api()
    try:
        user = twitch.get_users(logins=[broadcaster])["data"][0]
        return user['id']
    except BaseException as e:
        print(
            "Looks like that broad caster doesn't exist or your refresh token is bad. Try it again with a different token")
        sys.exit(1)