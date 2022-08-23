import sys
import traceback
from time import sleep

from Database.Twitch.twitch_clip_instance import add_twitch_clip_instance_from_api
from Database.Twitch.twitch_clip_instance_scan_job import add_twitch_clip_scan
from Events.flask_events import flask_event
from cloud_logger import cloud_logger, cloud_error_logger
from start_up_flask import rescanner
from twitch_helpers.twitch_helpers import get_twitch_api


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
        job_id = add_twitch_clip_scan(clip_id, clip_broadcaster)

        if job_id is not None:
            rescanner.add_job(job_id)
    except BaseException as e:
        cloud_error_logger(e, file=sys.stderr)
        traceback.print_exc()
