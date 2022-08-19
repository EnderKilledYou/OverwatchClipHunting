import json_fix
from flask import Blueprint
from Database.monitor import remove_stream_to_monitor, add_stream_to_monitor, get_all_my_monitors, get_all_monitors
from cloud_logger import cloud_error_logger
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
        my_monitors = get_all_monitors()
        if len(my_monitors) == 0:
            return {"success": True, 'items': []}
        user_list = list(map(lambda x: x.Broadcaster, my_monitors))
        twitch_api = get_twitch_api()
        streams = None  # cache.get('get_monitored_streams')
        if streams is None:
            streams = get_monitored_streams(twitch_api, user_list)
            # cache.set('get_monitored_streams', 30)
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
    remove_stream_to_monitor(stream_name)
    return {"success": True, 'items': []}
