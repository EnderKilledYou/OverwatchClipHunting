import os

import sys
import threading
import traceback

from Ocr.VideoCapReader import StreamEndedError, VideoCapReader
from Ocr.no_stream_error import NoStreamError
from Ocr.overwatch_readers.overwatch_screen_reader import OverwatchScreenReader
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

        """
        super(TwitchEater, self).__init__()

        self.items_read = None

        self.stream_res = ""
        self.reader = None
        self.broadcaster = broadcaster
        self.consumer_threads = []

        self._active = True

    def get_stats(self):
        if self.reader is None:
            return [1] * 8

        qsize = self.reader.count()
        frames_pending = qsize * self.reader.sample_every_count
        frames_finished = self.reader.items_drained * self.reader.sample_every_count
        back_fill_seconds = frames_pending // self.reader.fps

        return qsize, frames_finished, frames_finished, back_fill_seconds, self.reader.fps, self.reader.sample_every_count, self.reader.items_read, self.stream_res

    def get_one(self):
        if self.reader.count() == 0:
            return None
        item = self.buffer.get(False)
        self.reader.incr_items_drained()
        return item

    def join(self):
        for a in self.consumer_threads:
            a.join()

    def buffer_broadcast(self):

        wait_for_tesseract()

        best_stream = StreamLinkHelper.get_best_stream(self.broadcaster)
        if best_stream is None:
            return
        (ocr_stream, stream_res) = best_stream

        with OverwatchScreenReader(self) as matcher:
            self._consumers(matcher)
            self.stream_res = stream_res
            self.capture_url_or_file(ocr_stream.url)

    def _consumers(self, matcher: ScreenReader):
        # count = os.cpu_count()
        # print("Cpu threads would be " + str(count))
        # if count is None:
        count = 1
        for i in range(0, count):
            consumer_thread = threading.Thread(target=matcher.consume_twitch_broadcast)
            self.consumer_threads.append(consumer_thread)
            consumer_thread.start()

    def stop(self):
        print(f"stopping {self.broadcaster}")
        try:
            print(f"stopping - emptying buffer - {self.broadcaster}")
            while True:
                self.buffer.get(False)
        except:
            pass
        print(f"stopping - destroying reader - {self.broadcaster}")
        if hasattr(self, 'reader') and self.reader is not None:
            print(f"stopping - reader - {self.broadcaster}")
            self.reader.stop()
            print(f"stopping - destroyed reader - {self.broadcaster}")
        if hasattr(self, 'matcher') and self.matcher is not None:
            print(f"stopping - started matcher - {self.broadcaster}")
            self.matcher.stop()
            print(f"stopping - destroyed matcher - {self.broadcaster}")
        self._active = False

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        pass

    def __del__(self):
        print(f"TwitchEater Del")
        super().__del__()
        if hasattr(self, 'reader') and self.reader is not None:
            del self.reader
        if hasattr(self, 'matcher') and self.matcher is not None:
            del self.matcher
        if hasattr(self, 'buffer') and self.buffer is not None:
            del self.buffer


    def capture_url_or_file(self, url):
        self.reader = VideoCapReader(self.broadcaster)
        try:
            print(f'Capture thread starting {self.broadcaster}')
            self.reader.read(url, self.buffer)
            print(f'Capture thread releasing {self.broadcaster}')
        except StreamEndedError:
            print(f'Stream ended or buffer problem {self.broadcaster}')
            return
        except NoStreamError:
            print(f'Stream was not live {self.broadcaster}')
            return
        except BaseException as e:
            cloud_error_logger(e, file=sys.stderr)
            traceback.print_exc()
            return
        finally:
            self.stop()
        self._active = False
        print(f'Capture thread stopping {self.broadcaster} ...')
        self.join()
        print(f'Capture thread stopped {self.broadcaster}')
