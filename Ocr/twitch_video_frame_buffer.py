import os

import sys
import threading
import traceback

from Ocr.VideoCapReader import StreamEndedError, VideoCapReader
from Ocr.no_stream_error import NoStreamError
from Ocr.screen_reader import ScreenReader
from Ocr.stream_link_helper import StreamLinkHelper
from Ocr.video_frame_buffer import VideoFrameBuffer
from Ocr.wait_for_tessy import wait_for_tesseract
from cloud_logger import cloud_error_logger


class TwitchEater(VideoFrameBuffer):
    matcher: ScreenReader
    reader: VideoCapReader
    broadcaster: str = ''

    def __init__(self, broadcaster: str):
        """
            Manages the threads for a VideoCapReader.

        :param broadcaster:
        :param matcher:
        """
        super(TwitchEater, self).__init__()

        self.items_read = None
        self.matcher = None
        self.stream_res = ""
        self.reader = None
        self.broadcaster = broadcaster
        self.consumer_threads = []

        self._active = True

    def get_one(self):
        if self.reader.count() == 0:
            return None
        item = self.buffer.get(False)
        self.reader.incr_items_drained()
        return item

    def join(self):
        for a in self.consumer_threads:
            a.join()

    def buffer_broadcast(self, matcher: ScreenReader):
        self.matcher = matcher
        self._consumers(matcher)
        wait_for_tesseract()

        best_stream = StreamLinkHelper.get_best_stream(self.broadcaster)
        if best_stream is None:
            return
        (ocr_stream, stream_res) = best_stream

        self.stream_res = stream_res
        self.capture_url_or_file(ocr_stream.url)

    def _consumers(self, matcher: ScreenReader):
        count = os.cpu_count()
        print("Cpu threads would be " + str(count))
        # if count is None:
        # count = 1
        for i in range(0, count):
            consumer_thread = threading.Thread(target=matcher.consume_twitch_broadcast)
            self.consumer_threads.append(consumer_thread)
            consumer_thread.start()

    def stop(self):
        try:
            while True:
                self.buffer.get(False)
        except:
            pass
        if hasattr(self, 'reader') and self.reader is not None:
            self.reader.stop()
        if hasattr(self, 'matcher') and self.matcher is not None:
            self.matcher.stop()

    def __del__(self):
        if hasattr(self, 'reader') and self.reader is not None:
            del self.reader
        if hasattr(self, 'matcher') and self.matcher is not None:
            del self.matcher

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
            cloud_error_logger(e, file=sys.stderr)
            traceback.print_exc()
            return
        finally:
            self.matcher.Active = False
            self.reader.stop()

        print("Capture thread stopping")
