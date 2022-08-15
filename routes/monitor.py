from flask import Blueprint

from Ocr.tag_clipper import TagClipper

from Database.Twitch.tag_clipper_job import get_twitch_clip_job_by_clip_id, add_twitch_clip_job
from twitch_helpers import get_twitch_api

monitor = Blueprint('monitor', __name__)

from routes.monitor_manager import manager
from sharp_api import get_sharp

sharp = get_sharp()

tag_clipper = TagClipper()


@sharp.function()
def start_farm_twitch():
    manager.start_farm_twitch_mode()
    return {"success": True, }


@sharp.function()
def stop_farm_twitch():
    manager.stop_farm_twitch_mode()
    return {"success": True, }


@sharp.function()
def get_live_streamers():
    twitch_api = get_twitch_api()
    streams = twitch_api.get_streams(game_id="488552", language=['en'])
    return streams['data']


@sharp.function()
def add_tag_clipping(clip_id: str, tag_id: str):
    exists = get_twitch_clip_job_by_clip_id(clip_id, tag_id)
    if exists:
        return {"success": False, "error": "job already exists, try resettting it"}
    clip_scan = add_twitch_clip_job(clip_id, tag_id)
    return {"success": True, 'clip_scan': clip_scan}