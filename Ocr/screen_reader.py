from time import sleep

from Ocr.frames.frame import Frame

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

        while self.Active and self.framebuffer.active:
            frame = self.wait_next_frame()
            if frame is None:
                sleep(2)
                continue

            self.ocr(frame)

    def wait_next_frame(self):
        try:
            return self.framebuffer.get_one()
        except:
            return None
