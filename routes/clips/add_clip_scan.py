from Database.Twitch.twitch_clip_instance_scan_job import get_twitch_clip_scan_by_clip_id, add_twitch_clip_scan
from cloud_logger import cloud_logger
from routes.clips.clips import sharp


@sharp.function()
def add_clip_scan(clip_id: str):
    cloud_logger()
    exists = get_twitch_clip_scan_by_clip_id(clip_id)
    if exists:
        return {"success": False, "error": "Job already exists, try resetting it"}
    clip_scan = add_twitch_clip_scan(clip_id)
    return {"success": False, 'clip_scan': clip_scan}
