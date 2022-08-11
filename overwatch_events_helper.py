import json
import os.path
import threading

from flask_events import flask_event
from Ocr.frame import Frame
from Clipper.clip_timestamp import ClipTimeStamp
from in_flask import in_flask
from config.streamer_configs import get_streamer_config
from twitch_helpers import get_broadcaster_id, get_twitch_api

last_clip_time = {}



def create_clip(frame: Frame, clip_type: str):
    api = get_twitch_api()

    created = api.create_clip(get_broadcaster_id(frame.source_name), True)
    if not created:
        return
    if 'status' in created and created['created'] == 403:
        print("can't clip this channel no perms")
    if in_flask():
        flask_event.emit('clip', created['data'],clip_type)
    last_clip_time[frame.source_name] = frame.ts_second



    return created


def append_to_clip_log(clip_type, created, frame):
    if not os.path.exists('clip_log'):
        write_to_clip_log([])
    clip_data = read_clip_clog()

    clip_data.append({'streamer': frame.source_name,
                      'clip_data': created['data'],
                      'type': clip_type
                      })

    write_to_clip_log(clip_data)


def read_clip_clog():
    with open('clip_log', 'r') as clip_log:
        clip_data = json.loads(clip_log.read())
    return clip_data


def write_to_clip_log(clip_data):
    with open('clip_log', 'w') as clip_log:
        clip_log.write(json.dumps(clip_data))


def can_clip(frame, type: str):
    if not get_streamer_config(frame.source_name).make_clips:
        return False
    last_clip_distance = get_last_clip_time_distance(frame, type)
    if last_clip_distance < 30:
        print("Creating clips too soon " + type + " " + str(last_clip_distance))
        return False
    return True


def get_last_clip_time_distance(frame: Frame, type: str):
    index = type + "_" + frame.source_name
    if index not in last_clip_time:
        last_clip_time[index] = -30
    last_clip_distance = frame.ts_second - last_clip_time[index]
    return last_clip_distance


def create_elim_timestamp(frame: Frame, duration: int):
    clip_ts = ClipTimeStamp()
    clip_ts.start = frame.ts_second
    clip_ts.end = frame.ts_second + duration
    clip_ts.duration = duration
    clip_ts.type = 'elimination'
    return clip_ts
