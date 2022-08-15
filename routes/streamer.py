from flask import Blueprint

from routes.monitor_manager import manager

streamer = Blueprint('streamer', __name__)
from sharp_api import get_sharp

sharp = get_sharp()


@sharp.function()
def add(stream_name: str):
    if not manager.is_stream_monitored(stream_name):
        manager.add_stream_to_monitor(stream_name)
    for_web = manager.get_stream_monitors_for_web()
    return {"success": True, 'items': for_web}


@sharp.function()
def list():
    for_web = manager.get_stream_monitors_for_web()
    return {"success": True, 'items': for_web}


@sharp.function()
def remove(stream_name: str):
    if manager.is_stream_monitored(stream_name):
        manager.remove_stream_to_monitor(stream_name)

    for_web = manager.get_stream_monitors_for_web()
    return {"success": True, 'items': for_web}
