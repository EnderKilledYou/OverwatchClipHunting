from flask import Blueprint
from Database.monitor import avoid_monitor
from Monitors.tag_clipper import TagClipper

from twitch_helpers.twitch_helpers import get_twitch_api

monitor = Blueprint('monitor', __name__)
from app import api_generator
sharp = api_generator
tag_clipper = TagClipper()


@sharp.function()
def start_farm_twitch():
    return {"success": True, }


@sharp.function()
def stop_farm_twitch():
    return {"success": True, }


@sharp.function()
def avoid_user(stream_name: str):
    avoid_monitor(stream_name)
    return {"success": True, }


@sharp.function()
def get_live_streamers():
    twitch_api = get_twitch_api()
    streams = twitch_api.get_streams(game_id="488552", language=['en'])
    return streams['data']
