import json
import os.path

from Database.avoid_monitor import avoid_monitor
from Events.flask_events import flask_event
from Ocr.frames.frame import Frame

from config.streamer_configs import get_streamer_config

from twitch_helpers.twitch_helpers import get_twitch_api, get_broadcaster_id

last_clip_time = {}


def format_event_for_marker(event_type: str, start_seconds: int, end_seconds: int, special: str = ''):
    return f'{event_type} {special} {start_seconds} - {end_seconds}'


def create_clip(frame: Frame, clip_type: str):
    api = get_twitch_api()
    print(f"creating clip for {frame.source_name} {clip_type}")
    created = api.create_clip(get_broadcaster_id(frame.source_name), True)
    if created is None:
        print(f"could not create clip for {frame.source_name}")
        return

    if 'status' in created and created['status'] == 403:
        print("can't clip this channel no perms")
        avoid_monitor(frame.source_name)


    if 'data' in created:
        flask_event.emit('clip', created['data'], clip_type)
        set_last_clip_time(frame)
        return created
    print("got odd response")
    print(created)


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
    last_clip_distance = get_last_clip_time_distance(frame)
    if type == 'slept':
        last_clip_distance = last_clip_distance * 4
    if last_clip_distance < 30:
        print(f"Creating clips too soon {type} {str(last_clip_distance)}")
        return False
    return True


def set_last_clip_time(frame: Frame):
    last_clip_time[frame.source_name] = frame.ts_second


def get_last_clip_time_distance(frame: Frame):
    if frame.source_name not in last_clip_time:
        last_clip_time[frame.source_name] = -30
    distance = frame.ts_second - last_clip_time[frame.source_name]

    return distance
