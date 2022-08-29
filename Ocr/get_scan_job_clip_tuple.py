import sys
import traceback

from Database.Twitch.twitch_clip_instance import get_twitch_clip_instance_by_video_id, get_twitch_clip_video_id_by_id
from Database.Twitch.twitch_clip_instance_scan_job import TwitchClipInstanceScanJob, update_scan_job_started, \
    update_scan_job_error
from cloud_logger import cloud_error_logger


def get_scan_job_clip_tuple( job_id: int):
    try:
        job: TwitchClipInstanceScanJob = update_scan_job_started(job_id)
    except BaseException as e:
        cloud_error_logger(e, file=sys.stderr)
        traceback.print_exc()
        return None, None
    if job is None:
        return None, None
    try:
        clip = get_twitch_clip_instance_by_video_id(get_twitch_clip_video_id_by_id(job.clip_id))
    except BaseException as e:
        cloud_error_logger(e, file=sys.stderr)
        traceback.print_exc()
        return None, None
    if clip is None:
        update_scan_job_error(job.id, "Clip was not found")
        return None, None

    return job, clip
