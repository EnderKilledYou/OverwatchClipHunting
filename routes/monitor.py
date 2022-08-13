import traceback
from dateutil.parser import isoparse
from flask import jsonify, Blueprint
from flask_events import flask_event

from monitor_manager import  MonitorManager
from config.db_config import db
from login_dec import requires_logged_in, requires_admin_user
from routes.query_helper import get_query_by_page
from twitch.twitch_video import TwitchClipLog
from twitch_helpers import get_twitch_api

monitor = Blueprint('monitor', __name__)
from sharp_api import get_sharp

sharp = get_sharp()

manager = MonitorManager()

@requires_admin_user()
@sharp.function()
def add(stream_name :str):
    if not manager.is_stream_monitored(stream_name):
        manager.add_stream_to_monitor(stream_name)
    for_web = manager.get_stream_monitors_for_web()
    return {"success": True, 'items': for_web}
    # return twitch_oauth.authorize(callback=url_for('twitch.authorized', _external=True))


@sharp.function()
def list():
    for_web = manager.get_stream_monitors_for_web()
    return {"success": True, 'items': for_web}


@sharp.function()
def remove(stream_name:str):
    if manager.is_stream_monitored(stream_name):
        manager.remove_stream_to_monitor(stream_name)

    for_web = manager.get_stream_monitors_for_web()
    return {"success": True, 'items': for_web}


@sharp.function()
def deleteclips(clip_id:str):
    clip = TwitchClipLog.query.filter_by(id=int(clip_id)).first()
    if clip:
        db.session.delete(clip)
        db.session.commit()
        db.session.flush()

    return jsonify({"success": True})


@sharp.function()
def clips(creator_name:str, clip_type="", page=1):
    int_page = int(page)
    if clip_type == "all":
        query_filter_by = TwitchClipLog.query.filter_by(creator_name=creator_name, type=clip_type).order_by(
            TwitchClipLog.id.desc())

    else:
        query_filter_by = TwitchClipLog.query.filter_by(creator_name=creator_name).order_by(TwitchClipLog.id.desc())

    clips_response = get_query_by_page(query_filter_by, int_page)
    clip_list = query_to_list(clips_response)
    return jsonify({"success": True, 'items': clip_list})


@sharp.function()
def all_clips(clip_type="", page: int = 1):
    int_page = int(page)
    if clip_type == "all":
        filter_by = TwitchClipLog.query.filter_by().order_by(TwitchClipLog.id.desc())
    else:
        filter_by = TwitchClipLog.query.filter_by(type=clip_type).order_by(TwitchClipLog.id.desc())

    clips_response = get_query_by_page(filter_by, int_page)
    clip_list = query_to_list(clips_response)

    return jsonify({"success": True, 'items': clip_list})


def query_to_list(clips_response):
    clip_list = []
    for i in clips_response:
        clip_list.append(i.to_dict())
    return clip_list


@flask_event.on('clip')
def store_clip(clip_data, type):
    try:
        log = TwitchClipLog()
        clip = get_twitch_api().get_clips(clip_id=clip_data[0]["id"])
        if len(clip["data"]) == 0:
            print("couldn't get clip")
            return
        data = clip["data"][0]
        log.video_id = data['id']
        log.created_at = isoparse(data['created_at'])
        log.creator_name = data['creator_name']
        log.title = data['title']
        log.video_url = data['url']
        log.thumbnail_url = data['thumbnail_url']
        log.broadcaster_name = data['broadcaster_name']
        log.type = type
        db.session.add(log)
        db.session.commit()
        db.session.flush()
    except BaseException as e:
        print(e)
        traceback.print_exc()
