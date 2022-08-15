from flask import Blueprint

from Ocr.tag_clipper import TagClipper

from Database.Twitch.tag_clipper_job import get_twitch_clip_job_by_clip_id, add_twitch_clip_job
from twitch_helpers import get_twitch_api

monitor = Blueprint('monitor', __name__)

from sharp_api import get_sharp

sharp = get_sharp()

tag_clipper = TagClipper()


@sharp.function()
def get_live_streamers():
    twitch_api = get_twitch_api()
    streams = twitch_api.get_streams(game_id="488552")
    return streams['data']


@sharp.function()
def add_tag_clipping(clip_id: str, tag_id: str):
    exists = get_twitch_clip_job_by_clip_id(clip_id, tag_id)
    if exists:
        return {"success": False, "error": "job already exists, try resettting it"}
    clip_scan = add_twitch_clip_job(clip_id, tag_id)
    return {"success": False, 'clip_scan': clip_scan}
