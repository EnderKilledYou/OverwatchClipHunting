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
    update_scan_job_percent, update_scan_job_started, update_scan_job_in_scanning
from Ocr.clip_to_tag import clip_tag_to_clip

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

        try:

            job: TwitchClipInstanceScanJob = update_scan_job_started(job_id)
            if job is None:
                return
            path = tmp_path + os.sep + next(tempfile._get_candidate_names()) + '.mp4'
            self._scan_and_bam(job, path)
            Timer(8, clip_tag_to_clip, (job.clip_id, path, job.id)).start()
        except BaseException as e:
            cloud_error_logger(e, file=sys.stderr)
            traceback.print_exc()
            if job is not None:
                update_scan_job_error(job.id, str(e))

    def _scan_and_bam(self, job: TwitchClipInstanceScanJob, path: str):
        reader_buffer = Queue()

        url = self._get_url(job)
        if url is None:
            return

        _download_clip(url, Args(url, path))
        self._read(job, path, reader_buffer)

        update_twitch_clip_instance_filename(job.clip_id, path)
        update_scan_job_in_scanning(job.id)
        frames = queue_to_list(reader_buffer)
        frames.sort(key=attrgetter('frame_number'))
        self._scan_clip(job, frames)

    def _read(self, job, path, reader_buffer):
        reader = ClipVideoCapReader(job.broadcaster, job.clip_id)
        reader.read(path, reader_buffer)
        reader.stop()

    def _get_url(self, job: TwitchClipInstanceScanJob):
        video_id = get_twitch_clip_video_id_by_id(job.clip_id)
        if video_id is None:
            return None
        return video_id

    def _stop(self):
        if self._reader is not None:
            self._reader.stop()

    def _scan_clip(self, job: TwitchClipInstanceScanJob, reader_list):
        size = len(reader_list)
        frame_number = 0
        try:
            with PyTessBaseAPI(path=tess_fast_dir) as api:
                for frame in reader_list:
                    self.matcher.ocr(frame,api)
                    self._frame_count += 1
                    frame_number = frame_number + 1
                    percent_done = frame_number / size
                    i = int(percent_done * 100.0)
                    if i > 0 and i % 15 == 0:
                        update_scan_job_percent(job.id, percent_done)

        except BaseException as b:
            traceback.print_exc()
            pass

        update_scan_job_percent(job.id, 1)


def queue_to_list(queue: Queue):
    items = []
    try:
        while True:
            items.append(queue.get(False))
    except Empty:
        pass
    return items
