from flask import Blueprint

from Database.monitor import remove_stream_to_monitor, add_stream_to_monitor


streamer = Blueprint('streamer', __name__)
from sharp_api import get_sharp

sharp = get_sharp()


@sharp.function()
def add(stream_name: str):
    add_stream_to_monitor(stream_name)
    return {"success": True, 'items': []}


@sharp.function()
def list():

    return {"success": True, 'items': []}


@sharp.function()
def remove(stream_name: str):
    remove_stream_to_monitor(stream_name)

    return {"success": True, 'items': []}
