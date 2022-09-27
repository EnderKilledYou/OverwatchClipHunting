import re

import requests
from flask import request, Response, Blueprint

from Ocr.frames.frame import Frame
from Ocr.frames.ordered_frame_aggregator import OrderedFrameAggregator
from routes.frame_watcher_manager import clip_frame_watchers

callback = Blueprint('callback', __name__)


# frame_watchers[streamer] = OrderedFrameAggregator(overwatch_event)


@callback.route('/clip_scan_update')
def clip_scan_update(clip_token: str, frame: Frame, event_type: str):
    if frame is None:
        return
    if event_type is None:
        return
    if clip_token is None:
        return
    streamer = frame.source_name
    if streamer not in clip_frame_watchers:
        return
    frame_watcher: OrderedFrameAggregator
    (token, frame_watcher) = clip_frame_watchers[streamer]
    if token != clip_token:
        return
    if event_type == "elim":
        frame_watcher.add_elim_frame(event_type)
        return
    if event_type == "elimed":
        frame_watcher.add_elimed_frame(event_type)
        return
    if event_type == "slept":
        frame_watcher.add_slepting_frame(event_type)
        return
    if event_type == "defense":
        frame_watcher.add_defense_frame(event_type)
        return
    if event_type == "healing":
        frame_watcher.add_healing_frame(event_type)
        return
    if event_type == "orbed":
        frame_watcher.add_orb_gained_frame(event_type)
