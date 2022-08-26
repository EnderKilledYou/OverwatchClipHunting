import sys
import threading
import traceback
from queue import Queue

from Ocr.VideoCapReader import StreamEndedError, VideoCapReader
from Ocr.clear_queue import clear_queue
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
        self.broadcaster = broadcaster
        self.consumer_threads = []
        self._active = True
        self._last_stats = None

    def get_stats(self):
        if self._last_stats is None:
            return [1] * 8

        # qsize = self.reader.count()
        # frames_pending = qsize * self.reader.sample_every_count
        # frames_finished = self.reader.items_drained * self.reader.sample_every_count
        # back_fill_seconds = frames_pending // self.reader.fps
        #
        # self._last_stats = qsize, frames_finished, frames_finished, back_fill_seconds, self.reader.fps, self.reader.sample_every_count, self.reader.items_read, self.stream_res
        return self._last_stats


    def join(self):
        for a in self.consumer_threads:
            a.join()

    def buffer_broadcast(self, cancel_token,broadcaster):

        wait_for_tesseract()

        best_stream = StreamLinkHelper.get_best_stream(self.broadcaster)
        if best_stream is None:
            return
        (url, stream_res) = best_stream
        buffer = Queue()
        with VideoCapReader(self.broadcaster) as reader:
            with OverwatchScreenReader(cancel_token) as matcher:
                self._consumers(matcher,buffer,reader)
                self.stream_res = stream_res
                try:
                    print(f'Capture thread starting {self.broadcaster}')
                    reader.read(url, buffer)
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
            del matcher
        del reader
        clear_queue(buffer, self.broadcaster)
        del buffer

    def _consumers(self, matcher: ScreenReader, reader,buffer):
        # count = os.cpu_count()
        # print("Cpu threads would be " + str(count))
        # if count is None:
        count = 2
        for i in range(0, count):
            consumer_thread = threading.Thread(target=matcher.consume_twitch_broadcast, args=[reader,buffer])
            self.consumer_threads.append(consumer_thread)
            consumer_thread.start()

    def stop(self):
        print(f"stopping {self.broadcaster}")
        self._active = False

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
        self.consumer_threads.clear()
        if hasattr(self, 'reader') and self.reader is not None:
            del self.reader
        if hasattr(self, 'matcher') and self.matcher is not None:
            del self.matcher
        if hasattr(self, 'buffer') and self.buffer is not None:
            del self.buffer

    def capture_url_or_file(self, url, reader):

        self._active = False
        print(f'Capture thread stopping {self.broadcaster} ...')
        self.join()
        print(f'Capture thread stopped {self.broadcaster}')


