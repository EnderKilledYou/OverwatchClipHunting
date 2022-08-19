from twitchAPI.twitch import Twitch

from Database.Twitch.twitch_user import TwitchUser
from config.config import consumer_secret, consumer_key
from Database.Twitch.twitch_response import TwitchResponse
from Database.Twitch.twitch_video import TwitchVideo


def get_current_user(resp: TwitchResponse) -> TwitchUser:
    twitch = Twitch(app_id=consumer_key, app_secret=consumer_secret)
    twitch.set_user_authentication(resp.access_token, [], resp.refresh_token)

    users = twitch.get_users()
    user_dict = users['data'][0]
    return TwitchUser(user_dict)


def get_user_vods(resp: TwitchResponse, user_id):
    twitch = Twitch(app_id=consumer_key, app_secret=consumer_secret)
    twitch.set_user_authentication(resp.access_token, [], resp.refresh_token)
    videos = twitch.get_videos(user_id=user_id)
    videos_data_ = videos["data"]
    iterable = map(lambda x: TwitchVideo(x), videos_data_)
    return list(iterable)




