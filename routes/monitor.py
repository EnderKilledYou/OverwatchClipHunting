from flask import Blueprint

from routes.login_dec import check_admin
from routes.route_cache import cache

monitor = Blueprint('monitor', __name__)

from twitch_helpers.twitch_helpers import get_twitch_api
from Database.avoid_monitor import avoid_monitor
from app import api_generator

sharp = api_generator


@sharp.function()
def avoid_user(stream_name: str):
    check_admin()
    avoid_monitor(stream_name)
    return {"success": True, }


@sharp.function()
def get_live_streamers():
    if cache.has('get_live_streamers'):
        streams = cache.get('get_live_streamers')
        return streams

    twitch_api = get_twitch_api()
    streams = twitch_api.get_streams(game_id="488552", language=['en'])
    if 'data' in streams:
        cache.set(get_live_streamers, streams['data'])
        return streams['data']
    return {"error":"Could not get twitch"}
