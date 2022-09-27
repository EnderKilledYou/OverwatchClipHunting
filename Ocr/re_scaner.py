import os
import subprocess

import sys

import traceback
from os.path import abspath

from random import Random

from twitchdl.commands.download import get_clip_authenticated_url

from Database.Twitch.twitch_clip_instance import get_twitch_clip_video_id_by_id

from Database.Twitch.twitch_clip_instance_scan_job import update_scan_job_error, \
    update_scan_job_percent

from Ocr.get_scan_job_clip_tuple import get_scan_job_clip_tuple

from Ocr.rescanner_clip_merger import merge_clip_parts

from Ocr.VideoCapReader import VideoCapReader
from Ocr.wait_for_tessy import wait_for_tesseract
from cloud_logger import cloud_logger, cloud_error_logger
from generic_helpers.something_manager import ThreadedManager
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
        return None
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
            sub = subprocess.Popen([""])

            (output, err) = p.communicate()

            # This makes the wait possible
            p_status = p.wait()

            merge_clip_parts(clip)
            update_scan_job_percent(job_id, 1, True)

        except BaseException as e:
            cloud_error_logger(e, file=sys.stderr)
            traceback.print_exc()
            update_scan_job_error(job_id, str(e))


def get_clip_url(clip_id):
    twitch_video_id = get_twitch_clip_video_id_by_id(clip_id)
    if twitch_video_id is None:
        return None
    url = get_clip_authenticated_url(twitch_video_id, "source")
    if url is None:
        return None

    return url
