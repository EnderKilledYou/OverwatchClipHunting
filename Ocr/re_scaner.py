import os
import sys
import tempfile
import traceback
from operator import attrgetter
from os.path import abspath

from queue import Empty, Queue

import moviepy.config as mpy_conf
from twitchdl.commands.download import _download_clip

from Database.Twitch.twitch_clip_instance import get_twitch_clip_instance_by_id
from Database.Twitch.twitch_clip_instance_scan_job import TwitchClipInstanceScanJob, update_scan_job_error, \
    get_twitch_clip_scan_by_id, update_scan_job_percent, update_scan_job_started, update_scan_job_in_queue
from Ocr.twitch_dl_args import Args

mpy_conf.change_settings({'FFMPEG_BINARY': "C:\\ProgramData\\chocolatey\\bin\\ffmpeg.exe",
                          })

from Ocr.VideoCapReader import VideoCapReader, StreamEndedError, ClipVideoCapReader
from Ocr.overwatch_clip_reader import OverwatchClipReader
from something_manager import ThreadedManager
from Database.tag_and_bag import update_tag_and_bag_scan_progress, \
    if_tag_cancel_request_exists


class InvalidFpsError(BaseException):
    pass


tmp_path = abspath(
    './tmp')
if not os.path.exists(tmp_path):
    os.makedirs(tmp_path)


class RescannerRequest:
    def __init__(self, tag_id: int, mp4_url: str, broadcaster, clip_id: int):
        self.tag_id = tag_id
        self.broadcaster = broadcaster
        self.mp4_url = mp4_url
        self.clip_id = clip_id

        # self.reader = ClipVideoCapReader(self._broadcaster, clip_id)


class ReScanner(ThreadedManager):
    _frame_count: int
    _reader: VideoCapReader

    # self._instance.thumbnail_url.split("-preview", 1)[0] + ".mp4"
    def __init__(self):
        super(ReScanner, self).__init__(1)
        self._frame_count = 0
        self.matcher = OverwatchClipReader()

    def _do_work(self, job_id: int):
        try:
            reader_buffer = Queue()
            job: TwitchClipInstanceScanJob = update_scan_job_started(job_id)
            if job is None:
                return
            update_scan_job_in_queue(job.id)
            url = self._get_url(job)
            if url is None:
                return None
            path = tmp_path + os.sep + next(tempfile._get_candidate_names()) + '.mp4'
            _download_clip(url, Args(url, path))
            reader = ClipVideoCapReader(job.broadcaster, job.clip_id)
            reader.read(path, reader_buffer)
            reader.stop()


        except BaseException as e:
            print(e, file=sys.stderr)
            traceback.print_exc()
            if job is not None:
                update_scan_job_error(job.id, str(e))
            return
        finally:
            if path is not None:
                if os.path.exists(path):
                    os.unlink(path)
        try:
            frames = queue_to_list(reader_buffer)
            frames.sort(key=attrgetter('frame_number'))
            self._scan_clip(job, frames)
        except BaseException as e:
            print(e, file=sys.stderr)
            traceback.print_exc()
            update_scan_job_error(job.id, str(e))
            return

    def _get_url(self, job: TwitchClipInstanceScanJob):
        clip = get_twitch_clip_instance_by_id(job.clip_id)
        if clip is None:
            return None
        return clip.video_id

    def _stop(self):
        self._reader.stop()

    def _scan_clip(self, job: TwitchClipInstanceScanJob, reader_list):
        size = len(reader_list)
        frame_number = 0
        try:
            for frame in reader_list:
                self.matcher.ocr(frame)
                self._frame_count += 1
                frame_number = frame_number + 1
                percent_done = frame_number / size
                i = int(percent_done * 100.0)
                if i > 0 and i % 15 == 0:
                    update_scan_job_percent(job.id, percent_done)

        except BaseException as b:
            traceback.print_exc()
            pass

        update_scan_job_percent(job.id, 1, True)


def queue_to_list(queue: Queue):
    items = []
    try:
        while True:
            items.append(queue.get(False))
    except Empty:
        pass
    return items
