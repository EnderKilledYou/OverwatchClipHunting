from Ocr.frame import Frame
from clip_timestamp import ClipTimeStamp
from config.streamer_configs import get_streamer_config
from twitch_helpers import get_broadcaster_id, get_twitch_api

last_clip_time = {}


def create_clip(frame: Frame):
    created = get_twitch_api().create_clip(get_broadcaster_id(frame.source_name))
    last_clip_time[frame.source_name] = frame.ts_second
    return created


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
