import os
from queue import Empty

from time import sleep

from tesserocr import PyTessBaseAPI, PSM, OEM

from Ocr.frames.frame import Frame
from cloud_logger import cloud_error_logger
from config.config import tess_fast_dir


class ScreenReader:
    def __init__(self):
        self.Active = True
        self._gathered = 0

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.__del__()

    def ocr(self, frame: Frame, api: PyTessBaseAPI) -> None:
        """Load in the frame for extracting text."""
        pass

    def stop(self):
        self.Active = False

    def __del__(self):
        print(f"ScreenReader Del")
        self.Active = False
        self.framebuffer = None

    def consume_twitch_broadcast(self, cancel_token, reader, buffer):
        while not cancel_token.canelled:
            with PyTessBaseAPI(path=tess_fast_dir, psm=PSM.SINGLE_COLUMN, oem=OEM.LSTM_ONLY) as api:
                try:
                    while self.next_frame(api, reader, buffer):
                        pass
                except BaseException as b:
                    cloud_error_logger(b)
                api.Clear()
                api.ClearAdaptiveClassifier()
                api.ClearPersistentCache()
                api.End()
                del api

    def next_frame(self, api, reader, buffer,frame_watcher):
        frame = self.wait_next_frame(reader, buffer)
        if frame is None:
            sleep(1)
            return True
        self.ocr(frame, api,frame_watcher)
        del frame
        return True

    def wait_next_frame(self, reader, buffer):
        try:
            read = buffer.get(False)
            reader.incr_items_drained()
            return read
        except Empty:
            pass
        except BaseException as b:
            print(f"Couldn't consume one for {self.framebuffer.broadcaster} : {str(b)}")
            return None
