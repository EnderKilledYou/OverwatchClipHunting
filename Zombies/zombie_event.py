import os
import threading

from Database.Twitch.twitch_clip_instance import TwitchClipInstance
from Database.Twitch.twitch_clip_tag import TwitchClipTag


class EventEmiter:
    pass


import requests

zombie_events = EventEmiter()


def send_to_zombie_server(path, data):
    r = requests.post(f'{os.environ}{path}', json=data)
    print(f"Status Code: {r.status_code}, Response: {r.json()}")


def report_zombie_tag(tag: TwitchClipTag, clip: TwitchClipInstance):
    if not is_zombie_mode():
        return
    threading.Thread(target=send_to_zombie_server, args=['/zombie_tag', {
        'clip': clip.to_dict(),
        'tag': tag.to_dict()
    }])
    pass


def report_zombie_clip(request: TwitchClipTag, clip: TwitchClipInstance):
    if not is_zombie_mode():
        return
    pass


def emit_zombie_event(*args):
    if is_zombie_mode():
        threading.Thread(target=zombie_events.emit, args=args).start()


def is_zombie_mode():
    return "zombie" in os.environ


@zombie_events.on('clip')
def clip(twitch_video_id: str):
    pass


def clip_tag(twitch_video_id: str, tag: TwitchClipTag):
    pass

