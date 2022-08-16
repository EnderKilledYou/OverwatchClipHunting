import threading
from queue import Queue

from Ocr.overwatch_screen_reader import OverwatchScreenReader
from Ocr.screen_reader import ScreenReader
from Ocr.twitch_video_frame_buffer import TwitchEater
from Ocr.video_frame_buffer import VideoFrameBuffer






class Monitor:
    ocr: VideoFrameBuffer
    broadcaster: str
    matcher: ScreenReader




    def __init__(self, broadcaster: str, web_dict = {}):
        print("Monitor Starting: " + broadcaster)
        self.broadcaster = broadcaster
        self.ocr = TwitchEater(broadcaster)
        self.matcher = OverwatchScreenReader(self.ocr)
        self.producer_thread = threading.Thread(target=self.ocr.buffer_broadcast, args=[self.matcher])
        self.producer_thread.start()
        self.web_dict =web_dict

    def dump(self):
        tmp = self.ocr.buffer
        self.ocr.buffer = Queue()
        while not tmp.empty():
            try:
                tmp.get(False)
            finally:
                return

    def stop(self):
        self.ocr.stop()
        self.matcher.stop()

    def wait_for_stop(self, timeout=None):
        self.producer_thread.join(timeout)
