import os

import sys
import threading
import traceback
from os.path import abspath
from queue import Queue
from random import Random
from time import sleep

import cancel_token
from twitchdl.commands.download import get_clip_authenticated_url
from twitchdl.twitch import GQLError

from Database.Twitch.twitch_clip_instance import get_twitch_clip_video_id_by_id
from Database.Twitch.delete_twitch_clip import delete_clip
from Database.Twitch.twitch_clip_instance_scan_job import update_scan_job_error, \
    update_scan_job_percent, update_scan_job_in_scanning, update_scan_job_in_deepfacequeue
from Ocr.clear_queue import clear_queue
from Ocr.get_scan_job_clip_tuple import get_scan_job_clip_tuple
from Ocr.no_stream_error import NoStreamError
from Ocr.ocr_helpers import get_length
from Ocr.rescanner_clip_merger import merge_clip_parts

from Ocr.VideoCapReader import VideoCapReader, ClipVideoCapReader, StreamEndedError
from Ocr.wait_for_tessy import wait_for_tesseract
from cloud_logger import cloud_logger, cloud_error_logger
from generic_helpers.something_manager import ThreadedManager
from ocr_logic.ocr_logic import consume_twitch_clip
from ocr_logic.perma_ocr import PermaOCR


class InvalidFpsError(BaseException):
    pass


tmp_path = abspath(
    './tmp')
if not os.path.exists(tmp_path):
    os.makedirs(tmp_path)

rescanner_ocrs = [PermaOCR().start()]
rand = Random()


def get_scan_ocr():
    index = rand.randint(0, len(rescanner_ocrs) - 1)
    return rescanner_ocrs[index]


rescanner_ocr = PermaOCR().start()


class ReScanner(ThreadedManager):
    _frame_count: int
    _reader: VideoCapReader

    def __json__(self):
        return "rescanner"

    # self._instance.thumbnail_url.split("-preview", 1)[0] + ".mp4"
    def __init__(self):
        super(ReScanner, self).__init__(1)
        self._reader = None
        self._frame_count = 0

    def _do_work(self, job_id: int):

        cloud_logger()
        wait_for_tesseract()

        job, clip = get_scan_job_clip_tuple(job_id)
        if job is None:
            return None
        self._run(clip, job_id)
        del clip
        del job

    def _run(self, clip, job_id):
        try:

            url = get_clip_url(clip.id)
            if url is None:
                update_scan_job_error(job_id, "Clip was removed from twitch")
                return

            update_scan_job_in_scanning(job_id)
            self._scan_clip(job_id, clip.broadcaster_name, clip.id, url)
            update_scan_job_in_deepfacequeue(job_id)
            sleep(2)  # wait for all the items to have made
            merge_clip_parts(clip)
            update_scan_job_percent(job_id, 1, True)
        except GQLError as gql:
            update_scan_job_error(job_id, "Clip was removed from twitch")
            delete_clip(clip.id)
        except BaseException as e:
            cloud_error_logger(e, file=sys.stderr)
            traceback.print_exc()
            update_scan_job_error(job_id, str(e))

    def _on_frame_read(self, job_id, sample_every_count, size):

        def call_back(frame):
            if frame.frame_number % 20 == 0:
                count_size = (frame.frame_number * sample_every_count) / size
                update_scan_job_percent(job_id, count_size / 100)

        return call_back

    def _scan_clip(self, job_id: int, broadcaster: str, clip_id: int, path: str):
        cancel = cancel_token.CancellationToken()

        with ClipVideoCapReader(broadcaster, clip_id) as reader:
            frame_number = 0
            seconds = get_length(path)

            size = reader.fps * seconds
            buffer = Queue()
            threads = []
            try:
                for i in range(0, 2):
                    consumer_thread = threading.Thread(target=consume_twitch_clip,
                                                       args=[cancel, reader, buffer,
                                                             self._on_frame_read(job_id, reader.sample_every_count,
                                                                                 size)])
                    consumer_thread.start()
                    threads.append(consumer_thread)
                reader.read2(path, buffer, cancel)
                print(f'Capture thread releasing {broadcaster}')
            except StreamEndedError:
                print(f'Stream ended or buffer problem {broadcaster}')
            except NoStreamError:
                print(f'Stream was not live {broadcaster}')
            except BaseException as e:
                if 'icvExtractPattern' in str(e):
                    update_scan_job_error(job_id, "Url couldn't be read from twitch try hitting rescan.")
                    delete_clip(clip_id)
                    return
                cloud_error_logger(e, file=sys.stderr)
                traceback.print_exc()
                update_scan_job_error(job_id, str(e))
                return
            finally:
                clear_queue(buffer, broadcaster)
                cancel.cancel()
                reader.stop()
                print(f'waiting for clip reader of {broadcaster} {job_id}  to wind down')
                for consumer_thread in threads:
                    consumer_thread.join(20)
                    if consumer_thread.is_alive():
                        print(f'Clip reader of didnt end yet check for issue {broadcaster}  {job_id} down')
                print(f'Clip reader of {broadcaster}  {job_id} down')
                del buffer
        update_scan_job_percent(job_id, 1)


def get_clip_url(clip_id):
    twitch_video_id = get_twitch_clip_video_id_by_id(clip_id)
    if twitch_video_id is None:
        return None
    url = get_clip_authenticated_url(twitch_video_id, "source")
    if url is None:
        return None

    return url
