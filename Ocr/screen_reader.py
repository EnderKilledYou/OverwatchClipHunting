from time import sleep

import pytesseract

from Ocr.frame import Frame

from Ocr.video_frame_buffer import VideoFrameBuffer


class ScreenReader:
    def __init__(self, framebuffer: VideoFrameBuffer):
        self.Active = True
        self.framebuffer = framebuffer

    def ocr(self, frame: Frame) -> None:
        """Load in the frame for extracting text."""
        pass

    def stop(self):
        self.Active = False

    def consume_twitch_broadcast(self):

        while self.Active and self.framebuffer._active:
            frame = self.wait_next_frame()
            if frame is None:
                continue

            self.ocr(frame)

    def wait_next_frame(self):
        try:
            return self.framebuffer.buffer.get(False)
        except BaseException as e:
            return None
