from cloud_logger import cloud_logger
from routes.clips.clips import sharp
from twitch_helpers.twitch_helpers import get_twitch_api


@sharp.function()
def get_game_ids():
    cloud_logger()
    twitch_api = get_twitch_api()
    games = twitch_api.get_top_games(first=100)
    data = games['data']
    return data
