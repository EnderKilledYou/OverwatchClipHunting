import os
from time import sleep

from tesserocr import PyTessBaseAPI

from Ocr.frames.frame import Frame

from Ocr.video_frame_buffer import VideoFrameBuffer
from config.config import tess_fast_dir


class ScreenReader:
    def __init__(self, framebuffer: VideoFrameBuffer):
        self.Active = True
        self.framebuffer = framebuffer
        self._gathered = 0

    def ocr(self, frame: Frame, api: PyTessBaseAPI) -> None:
        """Load in the frame for extracting text."""
        pass

    def stop(self):
        self.Active = False

    def consume_twitch_broadcast(self):
        with PyTessBaseAPI(path=tess_fast_dir) as api:
            while self.Active and self.framebuffer.active and self.next_frame(api):
                pass

    def next_frame(self, api):
        frame = self.wait_next_frame()
        if frame is None:
            sleep(os.cpu_count() * 2)
            return True

        self.ocr(frame, api)
        return True

    def wait_next_frame(self):
        try:


            if self.framebuffer.is_empty():
                return None
            return self.framebuffer.get_one()
        except:
            return None
