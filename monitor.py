import threading
from queue import Queue

from Ocr.frame_aggregator import FrameAggregator
from Ocr.ordered_frame_aggregator import OrderedFrameAggregator
from Ocr.overwatch_screen_reader import OverwatchScreenReader
from Ocr.screen_reader import ScreenReader
from Ocr.twitch_video_frame_buffer import TwitchVideoFrameBuffer
from Ocr.video_frame_buffer import VideoFrameBuffer
from config.streamer_configs import get_streamer_config
from frame_buffer import set_frame_buffer
from overwatch_events import overwatch_event


class Monitor:
    ocr: VideoFrameBuffer
    broadcaster: str
    agg: FrameAggregator
    matcher: ScreenReader

    def __init__(self, broadcaster: str, ):
        print("read starting " + broadcaster)
        self.broadcaster = broadcaster
        self.ocr = TwitchVideoFrameBuffer(broadcaster, get_streamer_config(broadcaster).max_frames_to_scan_per_second)
        self.ocr.frame_streamer_name = broadcaster
        set_frame_buffer(broadcaster, self.ocr)

        self.agg = OrderedFrameAggregator(overwatch_event)
        self.matcher = OverwatchScreenReader(self.ocr, self.agg)
        self.producer_thread = threading.Thread(target=self.ocr.watch_streamer, args=[])

        self.consumer_threads = []
        for i in range(0, 4):
            consumer_thread = threading.Thread(target=self.matcher.consume_twitch_broadcast)
            self.consumer_threads.append(consumer_thread)
        self.producer_thread.start()

        for consumer_thread in self.consumer_threads:
            consumer_thread.start()

    def dump(self):
        tmp = self.ocr.buffer
        self.ocr.buffer = Queue()
        while not tmp.empty():
            try:
                tmp.get(False)
            finally:
                return

    def stop(self):
        self.ocr.Active = False
        self.matcher.Active = False
