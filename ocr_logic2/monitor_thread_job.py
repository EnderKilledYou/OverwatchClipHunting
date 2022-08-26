import gc
import sys
import threading
import traceback
from queue import Queue

from Database.monitor import Monitor, update_monitor_stats
from Database.unclaim_monitor import unclaim_table_type
from Ocr.VideoCapReader import VideoCapReader, StreamEndedError

from Ocr.no_stream_error import NoStreamError

from Ocr.stream_link_helper import StreamLinkHelper
from Ocr.clear_queue import clear_queue
from Ocr.wait_for_tessy import wait_for_tesseract
from cloud_logger import cloud_error_logger
from ocr_logic.ocr_logic import consume_twitch_broadcast
from threads.TableThreadJob import TableThreadJob


class MonitorThreadJob(TableThreadJob):

    def __init__(self, broadcaster):
        super(MonitorThreadJob, self).__init__(Monitor)
        self.broadcaster = broadcaster



    def _update_stats(self, stats):
        qsize, frames_finished, frames_finished, back_fill_seconds, fps, sample_every_count, items_read = stats
        try:
            stats_dict = {
                'frames_read': items_read * sample_every_count,
                'frames_done': frames_finished,
                'frames_read_seconds': frames_finished // fps,
                'back_fill_seconds': back_fill_seconds,
                'fps': fps,
                'queue_size': qsize,
                'stream_resolution': self.stream_res,

            }
            update_monitor_stats(self.broadcaster, stats_dict)
        except BaseException as b:
            cloud_error_logger(b)


    def _do_work(self, work: Monitor):

        wait_for_tesseract()
        print(f'Capture thread starting {self.broadcaster}')
        best_stream = StreamLinkHelper.get_best_stream(self.broadcaster)
        if best_stream is None:
            print(f'Capture thread stopping, no stream url {self.broadcaster}')
            return
        (url, stream_res) = best_stream
        self.stream_res = stream_res
        print(f'Capture thread stream found {stream_res} {self.broadcaster}')
        buffer = Queue()

        with VideoCapReader(self.broadcaster) as reader:

            for i in range(0, 2):
                consumer_thread = threading.Thread(target=consume_twitch_broadcast,
                                                   args=[self._cancel_token, reader, buffer])
                consumer_thread.start()
            try:
                reader.read2(url, buffer, self._cancel_token, self._update_stats)
                print(f'Capture thread releasing {self.broadcaster}')
            except StreamEndedError:
                print(f'Stream ended or buffer problem {self.broadcaster}')
            except NoStreamError:
                print(f'Stream was not live {self.broadcaster}')
            except BaseException as e:
                cloud_error_logger(e, file=sys.stderr)
                traceback.print_exc()
            finally:
                self._cancel_token.cancel()
        del reader
        clear_queue(buffer, self.broadcaster)
        del buffer
        print(f"Unclaiming for {work.broadcaster}")
        unclaim_table_type(Monitor, self._id)
        print(f"Unclaimed for {work.broadcaster}")
