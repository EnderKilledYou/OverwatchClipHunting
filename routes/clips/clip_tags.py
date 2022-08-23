from Database.Twitch.tag_clipper_job import add_twitch_clip_job
from cloud_logger import cloud_logger
from routes.clips.clips import sharp


@sharp.function()
def clip_tags(clip_id: int, tag_id: int):
    cloud_logger()
    clip_scan = add_twitch_clip_job(clip_id, tag_id)
    return {"success": True, 'clip_scan': clip_scan.to_dict()}
