from Events.overwatch_events import overwatch_event
from Ocr.frames.ordered_frame_aggregator import OrderedFrameAggregator

clip_frame_watchers = {}
live_frame_watchers = {}


def add_streamer_clip_watcher(streamer, token):
    if streamer not in clip_frame_watchers:
        clip_frame_watchers[streamer] = (token, OrderedFrameAggregator(overwatch_event))
