from Database.Twitch.twitch_clip_instance_scan_job import get_twitch_clip_scan_by_page
from cloud_logger import cloud_logger
from routes.clips.clips import sharp


@sharp.function()
def get_clip_scan_jobs(page: int = 1):
    try:
        cloud_logger()
        by_page = get_twitch_clip_scan_by_page(page, 10)
        return {"success": True,
                'items': by_page}
    except BaseException as be:

        return {"success": False, 'error': str(be)}
