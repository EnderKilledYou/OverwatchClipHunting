import os
import sys
import threading
import traceback

from Ocr.VideoCapReader import StreamEndedError, VideoCapReader
from Ocr.no_stream_error import NoStreamError
from Ocr.screen_reader import ScreenReader
from Ocr.stream_link_helper import StreamLinkHelper
from Ocr.video_frame_buffer import VideoFrameBuffer


class TwitchEater(VideoFrameBuffer):
    reader: VideoCapReader
    broadcaster: str = ''

    def __init__(self, broadcaster: str):
        """
            Manages the threads for a VideoCapReader.

        :param broadcaster:
        :param matcher:
        """
        super(TwitchEater, self).__init__()

        self.stream_res = ""
        self.reader = None
        self.broadcaster = broadcaster
        self.consumer_threads = []


        self._active = True

    def get_one(self):
        item = self.buffer.get(False)
        self.reader.incr_items_drained()
        return item

    def join(self):
        for a in self.consumer_threads:
            a.join()

    def buffer_broadcast(self, matcher: ScreenReader):
        self.matcher = matcher
        self._consumers(matcher)

        (ocr_stream,stream_res) = StreamLinkHelper.get_best_stream(self.broadcaster)
        if ocr_stream is None:
            return
        self.stream_res = stream_res
        self.capture_url_or_file(ocr_stream.url)

    def _consumers(self, matcher: ScreenReader):
        count = os.cpu_count()
        if count is None:
            count = 4
        for i in range(0, count):
            consumer_thread = threading.Thread(target=matcher.consume_twitch_broadcast)
            self.consumer_threads.append(consumer_thread)
            consumer_thread.start()

    def stop(self):
        if self.reader:
            self.reader.stop()
        if self.matcher:
            self.matcher.stop()

    def capture_url_or_file(self, url):
        self.reader = VideoCapReader(self.broadcaster)
        try:
            print("Capture thread starting")
            self.reader.read(url, self.buffer)
            print("Capture thread releasing")
        except StreamEndedError:
            print("Stream ended or buffer problem")
            return
        except NoStreamError:
            print("Stream was not live")
            return
        except BaseException as e:
            print(e, file=sys.stderr)
            traceback.print_exc()
            return
        finally:
            self.matcher.Active = False
            self.reader.stop()

        print("Capture thread stopping")
