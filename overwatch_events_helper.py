from Ocr.frame import Frame
from config.config import make_clips
from twitch_helpers import get_broadcaster_id, get_twitch_api

last_clip_time = {}


def create_clip(frame: Frame):
    created = get_twitch_api().create_clip(get_broadcaster_id(frame.source_name))
    last_clip_time[frame.source_name] = frame.ts_second
    return created


def can_clip(frame):
    if not make_clips:
        return False
    last_clip_distance = get_last_clip_time_distance(frame)
    if last_clip_distance < 30:
        print("Creating clips too soon " + str(last_clip_distance))
        return False
    return True


def get_last_clip_time_distance(frame):
    if not frame.source_name in last_clip_time:
        last_clip_time[frame.source_name] = 0
    last_clip_distance = frame.ts_second - last_clip_time[frame.source_name]
    return last_clip_distance
