import sys
import traceback
from time import sleep
from typing import Optional, List

from dateutil.parser import isoparse
from flask import Blueprint

from Database.Twitch.twitch_clip_instance_scan_job import get_twitch_clip_scan_by_clip_id, add_twitch_clip_scan, \
    get_twitch_clip_scan_by_page
from cloud_logger import cloud_error_logger, cloud_logger
from twitch_helpers.twitch_helpers import get_twitch_api

clips = Blueprint('clips', __name__)
from Ocr.re_scaner import ReScanner

from Database.Twitch.twitch_clip_tag import TwitchClipTag
from Database.Twitch.get_tag_and_bag import get_tag_and_bag_by_clip_id

from config.db_config import db
from Events.flask_events import flask_event
from routes.utils import query_to_list

from routes.query_helper import get_query_by_page

from Database.Twitch.twitch_clip_instance import TwitchClipInstance, \
    get_twitch_clip_instance_by_video_id, add_twitch_clip_instance_from_api
from Database.Twitch.tag_clipper_job import add_twitch_clip_job
from app import api_generator

sharp = api_generator

rescanner = ReScanner()


@sharp.function()
def add_clip(clip_id: str):
    cloud_logger()
    twitch_api = get_twitch_api()
    clip_resp = twitch_api.get_clips(clip_id=clip_id)
    if len(clip_resp['data']) == 0:
        return {"success": False, "error": "clip doesn't on twitch"}
    clip = get_twitch_clip_instance_by_video_id(clip_id)
    if not clip:
        (clip_id, clip_broadcaster) = add_twitch_clip_instance_from_api(clip_resp['data'][0], 'elim')
    else:
        (clip_id, clip_broadcaster) = clip.id, clip.broadcaster_name
    job_id = add_twitch_clip_scan(clip_id, clip_broadcaster)
    if job_id is not None:
        rescanner.add_job(job_id)
        return {"success": True, "clip": dict(clip)}
    return {"success": False, "error": "Clip is alread being processed"}


@sharp.function()
def get_game_ids():
    cloud_logger()
    twitch_api = get_twitch_api()
    games = twitch_api.get_top_games(first=100)
    data = games['data']
    return data


@sharp.function()
def get_clip_scan_jobs(page: int = 1):
    try:
        cloud_logger()
        by_page = get_twitch_clip_scan_by_page(page, 10)
        return {"success": True,
                'items': by_page}
    except BaseException as be:

        return {"success": False, 'error': str(be)}


@sharp.function()
def add_clip_scan(clip_id: str):
    cloud_logger()
    exists = get_twitch_clip_scan_by_clip_id(clip_id)
    if exists:
        return {"success": False, "error": "Job already exists, try resetting it"}
    clip_scan = add_twitch_clip_scan(clip_id)
    return {"success": False, 'clip_scan': clip_scan}


@sharp.function()
def deleteclips(clip_id: str):
    cloud_logger()
    with db.session.begin():
        clip = TwitchClipInstance.query.filter_by(id=int(clip_id)).first()
        if clip:
            db.session.delete(clip)

    db.session.flush()

    return {"success": True}


@sharp.function()
def clip_tags(clip_id: int, tag_id: int):
    cloud_logger()
    clip_scan = add_twitch_clip_job(clip_id, tag_id)
    return {"success": True, 'clip_scan': clip_scan.to_dict()}


@sharp.function()
def search_twitch_clips(broadcaster: Optional[str] = None,
                        game_id: Optional[str] = None,
                        clip_id: Optional[List[str]] = None,

                        ended_at: Optional[str] = None,
                        started_at: Optional[str] = None,
                        after_cursor: Optional[str] = None,
                        before_cursor: Optional[str] = None):
    twitch_api = get_twitch_api(
    )
    try:
        cloud_logger()
        if started_at is not None:
            started_at = isoparse(started_at)
        if ended_at is not None:
            ended_at = isoparse(ended_at)
        broadcaster_id = parse_broadcaster_id(broadcaster, twitch_api)
        result = twitch_api.get_clips(broadcaster_id=broadcaster_id,
                                      game_id=game_id,
                                      clip_id=clip_id,
                                      before=before_cursor,
                                      after=after_cursor,
                                      ended_at=ended_at,
                                      started_at=started_at)
    except BaseException as b:
        return {"success": False, "error": str(b)}
    if not result:
        return {"success": False, "error": "something fucky no result maybe twitch ded?"}
    return {"success": True, 'api_result': result}


def parse_broadcaster_id(broadcaster, twitch_api):
    try:
        broadcaster_id = None
        if broadcaster is None:
            return None

        result2 = twitch_api.get_users(logins=[broadcaster])
        if len(result2['data']) > 0:
            broadcaster_id = result2['data'][0]['id']
        else:
            raise ValueError("No Such Streamer")
        return broadcaster_id
    except:
        pass
    return None


@sharp.function()
def tags_job(clip_id: int):
    cloud_logger()
    clip_scan = add_twitch_clip_scan(clip_id)
    return {"success": True, 'clip_scan': clip_scan.to_dict()}


@sharp.function()
def clips_search(creator_name: str, clip_type: List[str] = [], page: int = 1):
    cloud_logger()
    int_page = int(page)
    if int_page < 1:
        int_page = 1
    with db.session.begin():
        q = TwitchClipInstance.query.join(TwitchClipTag,
                                          TwitchClipInstance.id == TwitchClipTag.clip_id, isouter=False).with_entities(
            TwitchClipInstance, TwitchClipTag)

        if len(clip_type) > 0:
            q = q.filter(TwitchClipTag.tag.in_(clip_type))

        if len(creator_name) > 0:
            q = q.filter(TwitchClipInstance.broadcaster_name == creator_name)

        clip_dict = {}
        for a in q.order_by(TwitchClipInstance.id.desc()).limit(100).offset((int_page - 1) * 100):
            if a[1] is None:
                continue
            if a[0] not in clip_dict:
                clip_dict[a[0]] = (a[0].to_dict(), [])
            clip_dict[a[0]][1].append(a[1].to_dict())

    return {"success": True, 'items': list(clip_dict.values())}


@sharp.function()
def list_twitch_clips(page: int = 1):
    cloud_logger()
    int_page = int(page)
    with db.session.begin():
        filter_by = TwitchClipInstance.query.filter_by().order_by(TwitchClipInstance.id.desc())
        clips_response = get_query_by_page(filter_by, int_page)
        tmp = []
        for clip in clips_response:
            tmp.append(clip.to_dict())
            db.session.expunge(clip)

    return {"success": True, 'items': tmp}


@sharp.function()
def all_clips(clip_type: str = "", page: int = 1):
    cloud_logger()
    int_page = int(page)
    with db.session.begin():
        if clip_type == "all":
            filter_by = TwitchClipInstance.query.filter_by()  # .order_by(TwitchClipLog.id.desc())
        else:
            filter_by = TwitchClipInstance.query.filter_by(type=clip_type).order_by(TwitchClipInstance.id.desc())

        clips_response = get_query_by_page(filter_by, int_page)

        clip_list = query_to_list(clips_response)
        resp_list = []
    for clip in clip_list:
        db.session.expunge(clip)
        tags = list(map(lambda x: x.to_dict(), get_tag_and_bag_by_clip_id(clip['id'])))
        resp_list.append((clip, tags))
    return {"success": True, 'items': resp_list}


@flask_event.on('clip')
def store_clip(clip_data, type):

    cloud_logger()
    try:
        clip = get_twitch_api().get_clips(clip_id=clip_data[0]["id"])
        if len(clip["data"]) == 0:
            sleep(15)
            clip = get_twitch_api().get_clips(clip_id=clip_data[0]["id"])
            if len(clip["data"]) == 0:
                print("couldn't get clip")
                return

        (clip_id, clip_broadcaster) = add_twitch_clip_instance_from_api(clip['data'][0], type)
        #job_id = add_twitch_clip_scan(clip_id, clip_broadcaster)

        # if job_id is not None:
        #     rescanner.add_job(job_id)
    except BaseException as e:
        cloud_error_logger(e, file=sys.stderr)
        traceback.print_exc()
