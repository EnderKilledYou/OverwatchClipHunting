import os
import traceback
from queue import Empty, Queue
from time import sleep

import cv2
import numpy
from PIL import Image

from Events.overwatch_clip_events import overwatch_clips_event
from Events.overwatch_events import overwatch_event
from Ocr.frames.frame import Frame
from Ocr.frames.frame_tester import FrameTester
from Ocr.frames.ordered_frame_aggregator import OrderedFrameAggregator
from Ocr.wait_for_tess import wait_for_tess
from config.config import tess_fast_dir
from ocr_logic.crop_center import crop
from ocr_logic.perma_ocr import get_perma_ocr


def _read_one_frame(buffer, frame_tester, frame_watcher, reader, return_queue, call_back=None):
    frame = wait_next_frame(reader, buffer)
    if frame is None:
        sleep(1)
        return
    job_tuple = (get_perma_ocr(), frame_watcher, frame_tester, return_queue)
    ocr(frame, job_tuple)
    if call_back is not None:
        call_back(frame)
    del frame
    frame = None


def consume_twitch_clip(cancel_token, reader, buffer, call_back=None):
    streamer_name = reader.streamer_name
    print(f"Starting consume_twitch_clip {streamer_name}")
    frame_watcher = OrderedFrameAggregator(overwatch_clips_event)
    return_queue = Queue()
    frame_tester = FrameTester()
    while not cancel_token.cancelled:
        try:
            _read_one_frame(buffer, frame_tester, frame_watcher, reader, return_queue, call_back)
        except BaseException as b:
            # cloud_error_logger(b)
            print(b)
            traceback.print_exception()
    print(f"stopping consume_twitch_clip {streamer_name}")
    print(f"stopped consume_twitch_clip {streamer_name}")
    try:
        return_queue.get(False)
    except:
        pass
    del frame_watcher
    del frame_tester
    cancel_token.cancel()


def consume_twitch_broadcast(cancel_token, reader, buffer):
    streamer_name = reader.streamer_name
    print(f"Starting consume_twitch_broadcast {reader.streamer_name}")
    frame_watcher = OrderedFrameAggregator(overwatch_event)
    return_queue = Queue()
    frame_tester = FrameTester()
    while not cancel_token.cancelled:
        try:
            _read_one_frame(buffer, frame_tester, frame_watcher, reader, return_queue)
        except BaseException as b:
            # cloud_error_logger(b)
            print(b)
            traceback.print_exception()
    print(f"stopping consume_twitch_broadcast {streamer_name}")
    print(f"stopped consume_twitch_broadcast {streamer_name}")
    try:
        return_queue.get(False)
    except:
        pass
    del frame_watcher
    del frame_tester
    cancel_token.cancel()


def ocr(frame: Frame, job_tuple) -> None:


    img_grey = cv2.cvtColor(frame.image, cv2.COLOR_RGB2GRAY)

    #edges = cv2.Canny(img_grey, 100, 200)
    pil_grey = Image.fromarray(img_grey)

    if frame.frame_number % 1000 == 0:
        print(f"Processing frame {frame.frame_number} for {frame.source_name}")
    process(pil_grey, frame, job_tuple)
    img_grey = None
    pil_grey = None
    edges = None


def wait_next_frame(reader, buffer):
    try:
        read = buffer.get(False)
        reader.incr_items_drained()
        return read
    except Empty:
        pass


def process(img: Image, frame: Frame, job_tuple):
    frame_tester: FrameTester
    api, frame_watcher, frame_tester, return_queue = job_tuple
    if not os.path.exists(tess_fast_dir):
        wait_for_tess()

    img_crop = crop(img)
    numpy_array = numpy.array(img_crop)
    cv2.imshow(frame.source_name, numpy_array)
    del numpy_array
    cv2.waitKey(25)
    text = api.GetUTF8Text(img_crop, return_queue)
    if len(text) > 5:
        print(text)
    if 'NATED' in text:
        print(text)
    img_crop = None
    frame.empty = True

    if len(text) < 4:
        text = None
        return
    frame_tester.test_overwatch_frame(frame, frame_watcher, text)
    text = None
