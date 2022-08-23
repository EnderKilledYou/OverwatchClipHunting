import os
import sys
import tempfile
import traceback
from operator import attrgetter
from os.path import abspath
from threading import Timer
from queue import Empty, Queue

from tesserocr import PyTessBaseAPI

from Database.Twitch.twitch_clip_instance import update_twitch_clip_instance_filename, \
    get_twitch_clip_video_id_by_id
from Database.Twitch.twitch_clip_instance_scan_job import TwitchClipInstanceScanJob, update_scan_job_error, \
    update_scan_job_percent, update_scan_job_started, update_scan_job_in_scanning, update_scan_job_in_deepfacequeue
from Ocr.ocr_helpers import get_length, clip_tag_to_clip, face_to_clip

from Ocr.twitch_dl_args import Args

from Ocr.VideoCapReader import VideoCapReader, ClipVideoCapReader
from Ocr.overwatch_readers.overwatch_clip_reader import OverwatchClipReader
from Ocr.vod_downloader import _download_clip
from Ocr.wait_for_tessy import wait_for_tesseract
from cloud_logger import cloud_logger, cloud_error_logger
from config.config import tess_fast_dir
from generic_helpers.something_manager import ThreadedManager


class InvalidFpsError(BaseException):
    pass


tmp_path = abspath(
    './tmp')
if not os.path.exists(tmp_path):
    os.makedirs(tmp_path)


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
        self.matcher = OverwatchClipReader()

    def _do_work(self, job_id: int):
        cloud_logger()
        wait_for_tesseract()
        job = None
        try:

            job: TwitchClipInstanceScanJob = update_scan_job_started(job_id)
            if job is None:
                return
            path = tmp_path + os.sep + next(tempfile._get_candidate_names()) + '.mp4'
            url = self._get_url(job)
            if url is None:
                return

            _download_clip(url, Args(url, path))

            update_twitch_clip_instance_filename(job.clip_id, path)
            update_scan_job_in_scanning(job.id)
            self._scan_clip(job, path)

            update_scan_job_in_deepfacequeue(job.id)
            Timer(0, face_to_clip, (job.clip_id, path, job.id)).start()


        except BaseException as e:
            cloud_error_logger(e, file=sys.stderr)
            traceback.print_exc()
            if job is not None:
                update_scan_job_error(job.id, str(e))

    def _get_url(self, job: TwitchClipInstanceScanJob):
        video_id = get_twitch_clip_video_id_by_id(job.clip_id)
        if video_id is None:
            return None
        return video_id

    def _stop(self):
        if self._reader is not None:
            self._reader.stop()

    def match_frame(self, itr, api):

        try:
            frame = next(itr)
            if frame is not None:
                with frame as frame__:
                    self.matcher.ocr(frame__, api)
        except StopIteration as st:
            return False
        except BaseException as b:
            return False
        return True

    def _scan_clip(self, job: TwitchClipInstanceScanJob, path: str):
        with ClipVideoCapReader(job.broadcaster, job.clip_id) as reader:
            # size = len(reader_list)
            frame_number = 0
            seconds = get_length(path)
            reader.sample_every_count = 10
            size = reader.fps * seconds / reader.sample_every_count
            try:
                itr = reader.readYield(path)
                with PyTessBaseAPI(path=tess_fast_dir) as api:
                    while self.match_frame(itr, api):
                        self._frame_count += 1
                        frame_number = frame_number + 1
                        self._update_percentage_in_row(frame_number, job, size)

            except BaseException as b:
                traceback.print_exc()
                pass

        update_scan_job_percent(job.id, 1)

    def _update_percentage_in_row(self, frame_number, job, size):
        if frame_number < size:
            percent_done = frame_number / size
        else:
            percent_done = .99  # we guessed the fps wrong (ffmped)
        i = int(percent_done * 100.0)
        if i > 0 and i % 15 == 0:
            update_scan_job_percent(job.id, percent_done)


def queue_to_list(queue: Queue):
    items = []
    try:
        while True:
            items.append(queue.get(False))
    except Empty:
        pass
    return items
