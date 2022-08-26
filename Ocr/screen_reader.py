import os
from queue import Empty

from time import sleep

from tesserocr import PyTessBaseAPI, PSM, OEM

from Ocr.frames.frame import Frame

from Ocr.video_frame_buffer import VideoFrameBuffer
from cloud_logger import cloud_error_logger
from config.config import tess_fast_dir


class ScreenReader:
    def __init__(self, framebuffer: VideoFrameBuffer):
        self.Active = True
        self.framebuffer = framebuffer
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
        pass

    def consume_twitch_broadcast(self):
        while self.framebuffer.active:
            with PyTessBaseAPI(path=tess_fast_dir, psm=PSM.SINGLE_COLUMN,oem=OEM.LSTM_ONLY) as api:
                try:
                    while self.next_frame(api) and self.framebuffer.active:
                        pass
                except BaseException as b:
                    cloud_error_logger(b)

    def next_frame(self, api):
        frame = self.wait_next_frame()
        if frame is None:
            sleep(1)
            return True

        self.ocr(frame, api)
        frame.image = None
        return True

    def wait_next_frame(self):
        try:
            return self.framebuffer.get_one()
        except Empty:
            pass
        except BaseException as b:
            print(f"Couldn't consume one for {self.framebuffer.broadcaster} : {str(b)}")
            return None
