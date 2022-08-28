import os

import sys
import tempfile
import traceback
from os.path import abspath
from queue import Empty, Queue
from random import random, Random
from time import sleep

import cancel_token
from tesserocr import PyTessBaseAPI
from twitchdl.twitch import GQLError

from Database.Twitch.get_tag_and_bag import get_tag_and_bag_by_clip_id, delete_tag_and_bag_by_id, \
    update_tag_and_bag_start_and_duration
from Database.Twitch.twitch_clip_instance import update_twitch_clip_instance_filename, \
    get_twitch_clip_video_id_by_id, get_twitch_clip_instance_by_video_id
from Database.Twitch.delete_twitch_clip import delete_clip
from Database.Twitch.twitch_clip_instance_scan_job import TwitchClipInstanceScanJob, update_scan_job_error, \
    update_scan_job_percent, update_scan_job_started, update_scan_job_in_scanning, update_scan_job_in_deepfacequeue
from Ocr.ocr_helpers import get_length, face_to_clip

from Ocr.twitch_dl_args import Args

from Ocr.VideoCapReader import VideoCapReader, ClipVideoCapReader
from Ocr.overwatch_readers.overwatch_clip_reader import OverwatchClipReader
from Ocr.vod_downloader import _download_clip
from Ocr.wait_for_tessy import wait_for_tesseract
from cloud_logger import cloud_logger, cloud_error_logger
from config.config import tess_fast_dir
from generic_helpers.something_manager import ThreadedManager
from ocr_logic.ocr_logic import PermaOCR


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

    def _get_path_url_tuple(self, clip, job_id):
        path = tmp_path + os.sep + next(tempfile._get_candidate_names()) + '.mp4'
        url = self._get_url(clip.id)
        if url is None:
            update_scan_job_error(job_id, "Couldn't get url")
            return None, None
        if clip.file_path is None or not os.path.exists(clip.file_path):
            try:
                _download_clip(url, Args(url, path))
            except GQLError as gql:
                update_scan_job_error(job_id, "Clip was removed from twitch")
                delete_clip(clip.id)
                return None, None
        else:
            path = clip.file_path

        path = path.strip()
        return path, url

    def _get_job_clip_tuple(self, job_id: int):
        try:
            job: TwitchClipInstanceScanJob = update_scan_job_started(job_id)
        except BaseException as e:
            cloud_error_logger(e, file=sys.stderr)
            traceback.print_exc()
            return None, None
        if job is None:
            return None, None
        try:
            clip = get_twitch_clip_instance_by_video_id(get_twitch_clip_video_id_by_id(job.clip_id))
        except BaseException as e:
            cloud_error_logger(e, file=sys.stderr)
            traceback.print_exc()
            return None, None
        if clip is None:
            update_scan_job_error(job.id, "Clip was not found")
            return None, None

        return job, clip
    def _do_work(self, job_id: int):
        cloud_logger()
        wait_for_tesseract()

        job, clip = self._get_job_clip_tuple(job_id)
        if job is None:
            return None
        self._run(clip, job_id)
        del clip
        del job


    def _run(self, clip, job_id):
        try:
            path, url = self._get_path_url_tuple()
            if path is None:
                return
            update_twitch_clip_instance_filename(clip.id, path)
            update_scan_job_in_scanning(job_id)
            self._scan_clip(job_id, clip.broadcaster_name, clip.id, path)

            update_scan_job_in_deepfacequeue(job_id)

            sleep(2)  # wait for all the items to have made
            self.merge_clip_parts(clip)
            update_scan_job_percent(job_id, 1, True)

        except BaseException as e:
            cloud_error_logger(e, file=sys.stderr)
            traceback.print_exc()
            update_scan_job_error(job_id, str(e))

    def merge_clip_parts(self, clip):
        clip_parts = get_tag_and_bag_by_clip_id(clip.id)
        clips_merged = {}
        for bag in clip_parts:
            if bag.tag not in clips_merged:
                clips_merged[bag.tag] = [bag]
                continue
            should_add = True
            for i in range(0, len(clips_merged[bag.tag])):
                existing_tag = clips_merged[bag.tag][i]
                if existing_tag.tag_start == bag.tag_start:
                    if existing_tag.tag_duration < bag.tag_duration:
                        delete_tag_and_bag_by_id(existing_tag.id)  # the clip is longer
                        clips_merged[bag.tag][i] = bag
                    else:
                        delete_tag_and_bag_by_id(bag.id)  # the existing clip is longer
                    should_add = False
                    break
                intersection = self.does_intersect_time(bag, existing_tag)

                if len(intersection) > 0:
                    duration_max, tag_min = self.get_new_start_end(bag, existing_tag)
                    existing_tag.tag_start = tag_min
                    duration_max_tag_min = duration_max - tag_min
                    existing_tag.tag_duration = duration_max_tag_min
                    update_tag_and_bag_start_and_duration(existing_tag.id, tag_min, duration_max_tag_min)
                    delete_tag_and_bag_by_id(bag.id)
                    should_add = False
                    break

            if should_add:
                clips_merged[bag.tag].append(bag)
        for item in clips_merged:
            clips_merged[item].clear()
        clips_merged.clear()

    def get_new_start_end(self, bag, existing_tag):
        clip_1_end = existing_tag.tag_start + existing_tag.tag_duration
        clip_2_end = bag.tag_start + bag.tag_duration
        tag_min = min(bag.tag_start, existing_tag.tag_start)
        duration_max = max(clip_1_end, clip_2_end)
        return duration_max, tag_min

    def does_intersect_time(self, bag, existing_tag):
        clip_1_end = existing_tag.tag_start + existing_tag.tag_duration
        clip_2_end = bag.tag_start + bag.tag_duration
        clip_1 = range(existing_tag.tag_start, clip_1_end + 2)
        clip_2 = range(bag.tag_start, clip_2_end + 2)
        xs = set(clip_1)
        intersection = xs.intersection(clip_2)
        return intersection

    def _get_url(self, clip_id):
        video_id = get_twitch_clip_video_id_by_id(clip_id)
        if video_id is None:
            return None
        return video_id

    def _stop(self):
        if self._reader is not None:
            self._reader.stop()

    def match_frame(self, itr, api, matcher: OverwatchClipReader):

        try:

            frame = next(itr)
            if frame is not None:
                with frame as frame__:
                    matcher.ocr(frame__, api)
        except StopIteration as st:
            return False
        except BaseException as b:
            return False
        return True

    def _scan_clip(self, job_id: int, broadcaster: str, clip_id: int, path: str):
        cancel = cancel_token.CancellationToken()
        with ClipVideoCapReader(broadcaster, clip_id) as reader:
            # size = len(reader_list)
            frame_number = 0
            seconds = get_length(path)
            reader.sample_every_count = 10
            size = reader.fps * seconds / reader.sample_every_count
            try:
                itr = reader.readYield(path, cancel)
                # with PyTessBaseAPI(path=tess_fast_dir) as api:
                with OverwatchClipReader() as matcher:
                    while self.match_frame(itr, get_scan_ocr(), matcher):
                        reader_count = reader.count()
                        if reader_count % 20 == 0:
                            count_size = reader_count / size
                            update_scan_job_percent(job_id, count_size / 100)

            except BaseException as b:
                traceback.print_exc()
                pass
            finally:
                cancel.cancel()
                reader.stop()
                del reader
        update_scan_job_percent(job_id, 1)


def queue_to_list(queue: Queue):
    items = []
    try:
        while True:
            items.append(queue.get(False))
    except Empty:
        pass
    return items
