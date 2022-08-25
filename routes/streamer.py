import json
import traceback

import json_fix
from flask import Blueprint

from Database.avoid_monitor import avoid_monitor
from Database.monitor import remove_stream_to_monitor, add_stream_to_monitor, get_all_my_monitors, get_all_monitors, \
    get_all_monitors_dicts
from cloud_logger import cloud_error_logger
from routes.login_dec import check_admin
from routes.route_cache import cache
from start_up_flask import alli
from twitch_helpers.get_monitored_streams import get_monitored_streams, get_monitored_streams_dicts
from twitch_helpers.twitch_helpers import get_twitch_api

streamer = Blueprint('streamer', __name__)
from app import api_generator

sharp = api_generator


@sharp.function()
def add(stream_name: str):
    check_admin()
    if add_stream_to_monitor(stream_name):
        cache.delete('my_monitors')
        cache.delete('get_monitored_streams')
    return {"success": True, 'items': []}


@sharp.function()
def list_streamers():
    try:
        if cache.has('my_monitors'):
           my_monitors = cache.get('my_monitors')
        else:
            my_monitors = get_all_monitors_dicts()
            cache.set('my_monitors', my_monitors,30)

        if len(my_monitors) == 0:
            return {"success": True, 'items': []}

        if cache.has('get_monitored_streams'):
            streams = cache.get('get_monitored_streams')
        else:
            twitch_api = get_twitch_api()
            streams = get_monitored_streams_dicts(twitch_api)
            cache.set('get_monitored_streams', streams,30)


        return {"success": True, 'items': [my_monitors, streams]}
    except BaseException as b:
        print(b)
        traceback.print_exc()
        cloud_error_logger(b)
        return {"error": str(b)}


def list_obj_to_list_dicts(my_monitors):
    list_obj_to_dict = list(map(lambda x: x.to_dict(), my_monitors))
    return list_obj_to_dict


@sharp.function()
def remove(stream_name: str):
    check_admin()
    avoid_monitor(stream_name)
    return {"success": True, 'items': []}
