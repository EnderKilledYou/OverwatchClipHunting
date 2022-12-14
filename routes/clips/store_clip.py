import sys
import traceback
from time import sleep

from Database.Twitch.twitch_clip_instance import add_twitch_clip_instance_from_api
from Database.Twitch.twitch_clip_instance_scan_job import add_twitch_clip_scan
from Database.avoid_monitor import avoid_monitor
from Events.flask_events import flask_event
from Events.system import system_events
from cloud_logger import cloud_logger, cloud_error_logger
from routes.login_dec import check_admin
from scanner import rescanner
from twitch_helpers.twitch_helpers import get_twitch_api


@flask_event.on('avoid')
def avoid_them(streamer_name):
    avoid_monitor(streamer_name)


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
            system_events.emit('rescan', job_id)

    except BaseException as e:
        cloud_error_logger(e, file=sys.stderr)
        traceback.print_exc()
