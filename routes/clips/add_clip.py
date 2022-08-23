from flask import session

from Database.Twitch.twitch_clip_instance import get_twitch_clip_instance_by_video_id, add_twitch_clip_instance_from_api
from Database.Twitch.twitch_clip_instance_scan_job import add_twitch_clip_scan
from cloud_logger import cloud_logger
from routes.clips.clips import sharp
from routes.login_dec import requires_admin_user, requires_logged_in
from start_up_flask import rescanner
from twitch_helpers.twitch_helpers import get_twitch_api


@requires_logged_in()
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
        return {"success": True,  }
    return {"success": False, "error": "Clip is alread being processed"}


@requires_admin_user()
@sharp.function()
def add_clip_admin(clip_id: str):
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
