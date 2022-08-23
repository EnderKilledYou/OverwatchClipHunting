import json_fix
from flask import Blueprint
from Database.monitor import remove_stream_to_monitor, add_stream_to_monitor, get_all_my_monitors, get_all_monitors
from cloud_logger import cloud_error_logger
from routes.route_cache import cache
from start_up_flask import alli
from twitch_helpers.get_monitored_streams import get_monitored_streams
from twitch_helpers.twitch_helpers import get_twitch_api

streamer = Blueprint('streamer', __name__)
from app import api_generator

sharp = api_generator


@sharp.function()
def add(stream_name: str):
    add_stream_to_monitor(stream_name)
    return {"success": True, 'items': []}


@sharp.function()
def list_streamers():
    try:
        my_monitors = cache.get('my_monitors')
        if my_monitors is None:
            my_monitors = get_all_monitors()
            cache.set('my_monitors', 120)
        if len(my_monitors) == 0:
            return {"success": True, 'items': []}

        twitch_api = get_twitch_api()
        streams = cache.get('get_monitored_streams')
        if streams is None:
            streams = get_monitored_streams(twitch_api)
            cache.set('get_monitored_streams', 120)
        dictsm = list_obj_to_list_dicts(my_monitors)
        dictss = list_obj_to_list_dicts(streams)
        return {"success": True, 'items': [dictsm, dictss]}
    except BaseException as b:
        cloud_error_logger(b)
        return {"error": str(b)}


def list_obj_to_list_dicts(my_monitors):
    list_obj_to_dict = list(map(lambda x: x.to_dict(), my_monitors))
    return list_obj_to_dict


@sharp.function()
def remove(stream_name: str):
    alli.stop_streamer(stream_name)

    return {"success": True, 'items': []}
