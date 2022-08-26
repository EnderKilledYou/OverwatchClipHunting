import sys
from queue import Empty
from time import sleep

import cv2
from PIL import Image

from tesserocr import PyTessBaseAPI, PSM, OEM

from Ocr.frames.frame import Frame
from Ocr.overwatch_readers.overwatch_action_screen_region import OverwatchActionScreenRegion
from Ocr.overwatch_readers.overwatch_screen_reader import OverwatchScreenReader
from cloud_logger import cloud_error_logger
from config.config import tess_fast_dir


def consume_twitch_broadcast(cancel_token, reader, buffer):
    while not cancel_token.cancelled:
        with OverwatchActionScreenRegion() as action_text_matcher:
            with PyTessBaseAPI(path=tess_fast_dir, psm=PSM.SINGLE_COLUMN, oem=OEM.LSTM_ONLY) as api:
                try:
                    while next_frame(api, reader, buffer, ocr, action_text_matcher):
                        pass
                except BaseException as b:
                    cloud_error_logger(b)

                api.Clear()
                api.ClearAdaptiveClassifier()
                api.ClearPersistentCache()



def next_frame(api, reader, buffer, ocr, action_text_matcher: OverwatchActionScreenRegion):
    frame = wait_next_frame(reader, buffer)
    if frame is None:
        sleep(1)
        return True
    ocr(frame, api,action_text_matcher)
    del frame
    return True


def ocr(frame: Frame, api: PyTessBaseAPI, action_text_matcher: OverwatchActionScreenRegion) -> None:
    try:
        img_grey = cv2.cvtColor(frame.image, cv2.COLOR_RGB2GRAY)
        pil_grey = Image.fromarray(img_grey)
        if frame.frame_number % 100 == 0:
            print(f"Processing frame {frame.frame_number} for {frame.source_name}")
        action_text_matcher.process(pil_grey, frame, api)
        del img_grey
        del pil_grey
        if frame.empty:
            del frame



    except BaseException as e:
        cloud_error_logger(e, file=sys.stderr)
        import traceback
        traceback.print_exc()


def wait_next_frame(reader, buffer):
    try:
        read = buffer.get(False)
        reader.incr_items_drained()
        return read
    except Empty:
        pass
