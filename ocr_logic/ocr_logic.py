import sys
from queue import Empty
from time import sleep

import cv2
from PIL import Image
from tesserocr import PyTessBaseAPI, PSM, OEM
from Ocr.frames.frame import Frame
from Ocr.overwatch_readers.overwatch_action_screen_region import OverwatchActionScreenRegion
from cloud_logger import cloud_error_logger
from config.config import tess_fast_dir


def consume_twitch_broadcast(cancel_token, reader, buffer):
    streamer_name = reader.streamer_name
    print(f"Starting consume_twitch_broadcast {streamer_name}")
    with PyTessBaseAPI(path=tess_fast_dir, psm=PSM.SINGLE_COLUMN, oem=OEM.LSTM_ONLY) as api:
        with OverwatchActionScreenRegion() as action_text_matcher:
            while not cancel_token.cancelled:
                try:
                    frame = wait_next_frame(reader, buffer)
                    if frame is None:
                        sleep(1)
                        continue
                    ocr(frame, api, action_text_matcher)
                    frame = None
                except BaseException as b:
                    cloud_error_logger(b)
        print(f"stopping consume_twitch_broadcast {streamer_name}")
    api.ClearPersistentCache()
    api.End()
    print(f"stopped consume_twitch_broadcast {streamer_name}")
    cancel_token.cancel()


def ocr(frame: Frame, api: PyTessBaseAPI, action_text_matcher: OverwatchActionScreenRegion) -> None:
    img_grey = cv2.cvtColor(frame.image, cv2.COLOR_RGB2GRAY)
    pil_grey = Image.fromarray(img_grey)
    if frame.frame_number % 100 == 0:
        print(f"Processing frame {frame.frame_number} for {frame.source_name}")
    action_text_matcher.process(pil_grey, frame, api)
    img_grey = None
    pil_grey = None
    frame.image = None


def wait_next_frame(reader, buffer):
    try:
        read = buffer.get(False)
        reader.incr_items_drained()
        return read
    except Empty:
        pass
