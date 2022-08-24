from Database.Twitch.twitch_clip_instance import TwitchClipInstance, get_twitch_clip_instance_by_id
from Database.Twitch.twitch_clip_instance_scan_job import get_twitch_clip_scan_by_page, get_twitch_clip_tag_by_id
from cloud_logger import cloud_logger
from routes.clips.clips import sharp


@sharp.function()
def get_clip_by_tag_id(tag_id: int):
    tag = get_twitch_clip_tag_by_id(tag_id)
    if tag is None:
        return {"success": False, 'error': 'No Such tag'}
    video = get_twitch_clip_instance_by_id(tag['clip_id'])
    if video is None:
        return {"success": False, 'error': 'Tag exists but video does not'}
    return {"success": False, 'video_id': video.id, 'tag': tag}


@sharp.function()
def get_clip_scan_jobs(page: int = 1):
    try:
        cloud_logger()
        by_page = get_twitch_clip_scan_by_page(page, 10)
        return {"success": True,
                'items': by_page}
    except BaseException as be:

        return {"success": False, 'error': str(be)}
