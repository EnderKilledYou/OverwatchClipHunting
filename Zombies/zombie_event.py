import os
import threading

from Database.Twitch.twitch_clip_tag import TwitchClipTag


class EventEmiter:
    pass


zombie_events = EventEmiter()


def emit_zombie_event(*args):
    if "zombie" in os.environ:
        threading.Thread(target=zombie_events.emit, args=args).start()


@zombie_events.on('clip')
def clip(twitch_video_id: str):
    pass


def clip_tag(twitch_video_id: str, tag: TwitchClipTag):
    pass
