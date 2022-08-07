from Ocr.frame import Frame
from config.config import make_clips
from twitch_helpers import get_broadcaster_id, get_twitch_api

last_clip_time = 0


def create_clip(frame: Frame):
    global last_clip_time
    created = get_twitch_api().create_clip(get_broadcaster_id(frame.source_name))
    last_clip_time = frame.ts_second
    return created


def can_clip(frame):
    if not make_clips:
        return False
    last_clip_distance = get_last_clip_time_distance(frame)
    if last_clip_distance < 10:
        print("Creating clips too soon " + str(last_clip_distance))
        return False
    return True


def get_last_clip_time_distance(frame):
    last_clip_distance = frame.ts_second - last_clip_time
    return last_clip_distance
