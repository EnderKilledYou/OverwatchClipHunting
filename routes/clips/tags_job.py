from Database.Twitch.twitch_clip_instance_scan_job import add_twitch_clip_scan
from cloud_logger import cloud_logger
from routes.clips.clips import sharp


@sharp.function()
def tags_job(clip_id: int):
    cloud_logger()
    clip_scan = add_twitch_clip_scan(clip_id)
    return {"success": True, 'clip_scan': clip_scan.to_dict()}
