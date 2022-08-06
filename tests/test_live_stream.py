import json

import cv2
import streamlink

from Ocr.frame import Frame
from Ocr.frame_aggregator import FrameAggregator
from Ocr.twitch_video_frame_buffer import TwitchVideoFrameBuffer
from twitch.twitch_response import TwitchResponse

items = []


def on_elim_event(frame: Frame, count: int, duration: int, last_death):
    pass


def on_elimed_event(frame: Frame, second: int):

    pass


def on_healed_event(frame: Frame, amount: int):
    pass


def on_spawn_room_event(frame: Frame, second: int):
    pass


agg = FrameAggregator(elim_call_back=on_elim_event, healed_call_back=on_healed_event, elimed_call_back=on_elimed_event,
                      spawned_call_back=on_spawn_room_event)

streams = streamlink.streams('https://www.twitch.tv/warn')
ocr = TwitchVideoFrameBuffer(None, 8, agg)

url = streams['best'].url
cap = cv2.VideoCapture(url)
ocr.buffer_twitch_broadcast(cap)
cap.release()
