import atexit
import traceback
from time import sleep
from typing import Optional, List

from dateutil.parser import isoparse
from flask import Blueprint
from sqlalchemy.orm import aliased
from sqlalchemy.orm.query import BulkUD

from Database.Twitch.twitch_clip_instance_scan_job import get_twitch_clip_scan_by_clip_id, add_twitch_clip_scan, \
    get_twitch_clip_scan_by_page
from Database.tag_and_bag import add_tag_and_bag_request

clips = Blueprint('clips', __name__)
from Ocr.re_scaner import ReScanner
from Ocr.rescanner_monitor import ReScannerMonitor, make_rescanner_job_from_clip_id
from Database.Twitch.twitch_clip_tag import get_tag_and_bag_by_clip_id, TwitchClipTag

from config.db_config import db
from flask_events import flask_event
from routes.utils import query_to_list

from routes.query_helper import get_query_by_page
from sharp_api import get_sharp
from Database.Twitch.twitch_clip_instance import TwitchClipInstance, \
    get_twitch_clip_instance_by_video_id, add_twitch_clip_instance_from_api, get_twitch_clip_instance_by_id
from Database.Twitch.tag_clipper_job import add_twitch_clip_job, reset_twitch_clip_job_state, requeue_twitch_clip_jobs
from twitch_helpers import get_twitch_api, twitch_api

sharp = get_sharp()

rescanner = ReScanner()
rescanner.start()

reset_twitch_clip_job_state()
requeue_twitch_clip_jobs(rescanner)

atexit.register(rescanner.stop)


@sharp.function()
def add_clip(clip_id: str):
    twitch_api = get_twitch_api()
    clip_resp = twitch_api.get_clips(clip_id=clip_id)
    if len(clip_resp['data']) == 0:
        return {"success": False, "error": "clip doesn't on twitch"}
    clip = get_twitch_clip_instance_by_video_id(clip_id)
    if not clip:
        clip = add_twitch_clip_instance_from_api(clip_resp['data'][0], 'elim')
    job = add_twitch_clip_scan(clip.id, clip.broadcaster_name)
    if job is not None:
        rescanner.add_job(job.id)
        return {"success": True, "clip": clip.to_dict()}
    return {"success": False, "error": "Clip is alread being processed"}


@sharp.function()
def get_game_ids():
    twitch_api = get_twitch_api()
    games = twitch_api.get_top_games(first=100)
    data = games['data']
    return data


@sharp.function()
def get_clip_scan_jobs(page: int = 1):
    try:

        by_page = get_twitch_clip_scan_by_page(page)
        return {"success": True,
                'items': list(map(lambda x: (x[0].to_dict(), x[1].to_dict()), by_page))}
    except BaseException as be:

        return {"success": False, 'error': str(be)}


@sharp.function()
def add_clip_scan(clip_id: str):
    exists = get_twitch_clip_scan_by_clip_id(clip_id)
    if exists:
        return {"success": False, "error": "Job already exists, try resetting it"}
    clip_scan = add_twitch_clip_scan(clip_id)
    return {"success": False, 'clip_scan': clip_scan}


@sharp.function()
def deleteclips(clip_id: str):
    clip = TwitchClipInstance.query.filter_by(id=int(clip_id)).first()
    if clip:
        db.session.delete(clip)
        db.session.commit()
        db.session.flush()

    return {"success": True}


# clip_queue = get_tag_and_bag_by_clip_id(clip.id)
# for a in clip_queue:
#     clip_scan = add_twitch_clip_job(a.clip_id, a.id)
#
# add_twitch_clip_scan(clip.id)
# job = get_twitch_clip_job()

@sharp.function()
def clip_tags(clip_id: int, tag_id: int):
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
        if started_at is not None:
            started_at = isoparse(started_at)
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
    clip_queue = get_tag_and_bag_by_clip_id(clip_id)
    clip_scan = add_twitch_clip_scan(clip_id)
    return {"success": True, 'clip_scan': clip_scan.to_dict()}


@sharp.function()
def clips_search(creator_name: str, clip_type: List[str] = [], page: int = 1):
    int_page = int(page)
    if int_page < 1:
        int_page = 1

    q = TwitchClipInstance.query.join(TwitchClipTag,
                                      TwitchClipInstance.id == TwitchClipTag.clip_id, isouter=False).with_entities(
        TwitchClipInstance, TwitchClipTag)

    if len(clip_type) > 0:
        q = q.filter(TwitchClipTag.tag.in_(clip_type))

    if len(creator_name) > 0:
        q = q.filter(TwitchClipInstance.broadcaster_name == creator_name)

    clips_response = q.limit(100).offset((int_page - 1) * 100).all()

    clip_dict = {}
    for a in q:
        if a[1] is None:
            continue
        if a[0] not in clip_dict:
            clip_dict[a[0]] = (a[0].to_dict(), [])
        clip_dict[a[0]][1].append(a[1].to_dict())

    return {"success": True, 'items': list(clip_dict.values())}


@sharp.function()
def all_clips(clip_type: str = "", page: int = 1):
    int_page = int(page)

    if clip_type == "all":
        filter_by = TwitchClipInstance.query.filter_by()  # .order_by(TwitchClipLog.id.desc())
    else:
        filter_by = TwitchClipInstance.query.filter_by(type=clip_type).order_by(TwitchClipInstance.id.desc())

    clips_response = get_query_by_page(filter_by, int_page)

    clip_list = query_to_list(clips_response)
    resp_list = []
    for clip in clip_list:
        tags = list(map(lambda x: x.to_dict(), get_tag_and_bag_by_clip_id(clip['id'])))
        resp_list.append((clip, tags))
    return {"success": True, 'items': resp_list}


@flask_event.on('clip')
def store_clip(clip_data, type):
    try:

        clip = get_twitch_api().get_clips(clip_id=clip_data[0]["id"])
        if len(clip["data"]) == 0:
            sleep(15)
            clip = get_twitch_api().get_clips(clip_id=clip_data[0]["id"])
            if len(clip["data"]) == 0:
                print("couldn't get clip")
                return
        clip = add_twitch_clip_instance_from_api(clip['data'][0], type)

        job = add_twitch_clip_scan(clip.id, clip.broadcaster_name)
        if job is not None:
            rescanner.add_job(job.id)
    except BaseException as e:
        print(e)
        traceback.print_exc()
