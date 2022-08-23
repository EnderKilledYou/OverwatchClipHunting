import os
import sys
import traceback
from os.path import abspath
from threading import Timer
from typing import List

from deepface import DeepFace

from AI.deep_face_result import DeepFaceResult
from Database.Twitch.twitch_clip_instance import TwitchClipInstance, get_twitch_clip_instance_by_id
from Database.Twitch.twitch_clip_instance_scan_job import update_scan_job_error, \
    update_scan_job_percent, update_scan_job_in_deepface, update_scan_job_in_subclip
from Database.Twitch.twitch_clip_tag import TwitchClipTag, add_twitch_clip_tag_request
from Ocr.ocr_helpers import get_length, clip_tag_to_clip

from Ocr.VideoCapReader import VideoCapReader, ClipVideoCapReader
from Ocr.overwatch_readers.overwatch_clip_reader import OverwatchClipReader
from Ocr.wait_for_tessy import wait_for_tesseract
from cloud_logger import cloud_logger, cloud_error_logger
from generic_helpers.something_manager import ThreadedManager


class InvalidFpsError(BaseException):
    pass


tmp_path = abspath(
    './tmp')
if not os.path.exists(tmp_path):
    os.makedirs(tmp_path)


def crop_by_region(frame, region):
    return frame


class DeepFacer(ThreadedManager):
    _frame_count: int

    def __json__(self):
        return "rescanner"

    # self._instance.thumbnail_url.split("-preview", 1)[0] + ".mp4"
    def __init__(self):
        super(DeepFacer, self).__init__(1)

        self._frame_count = 0
        self.matcher = OverwatchClipReader()

    def _do_work(self, job_tuple):
        cloud_logger()
        wait_for_tesseract()
        frames = []
        try:

            if job_tuple is None:
                return
            (clip_id, file, scan_job_id) = job_tuple
            update_scan_job_in_deepface(scan_job_id)
            clip: TwitchClipInstance = get_twitch_clip_instance_by_id(clip_id)

            frames: List[DeepFaceResult] = self._scan_clip(scan_job_id, file, clip.broadcaster_name.lower(),
                                                           clip_id)

            if frames is None:
                return

            self._calculate_emotion(clip_id, frames, 'happy')
            self._calculate_emotion(clip_id, frames, 'neutral')
            self._calculate_emotion(clip_id, frames, 'fear')
            self._calculate_emotion(clip_id, frames, 'sad')
            self._calculate_emotion(clip_id, frames, 'angry')
            self._calculate_emotion(clip_id, frames, 'disgust')
            for item in frames:
                del item
            frames.clear()
            update_scan_job_in_subclip(scan_job_id)
            Timer(8, clip_tag_to_clip, (clip_id, file, scan_job_id)).start()



        except BaseException as e:
            cloud_error_logger(e, file=sys.stderr)
            traceback.print_exc()
            update_scan_job_error(scan_job_id, str(e))
        finally:
            if frames is not None:
                frames.clear()

    def _calculate_emotion(self, clip_id, frames, emotion: str):
        if len(frames) == 0:
            return
        happy = list(map(lambda item: getattr(item.emotion, emotion), frames))
        _max = max(happy)
        _min = min(happy)
        max_frames = list(filter(lambda item: getattr(item.emotion, emotion) == _max, frames))
        min_frames = list(filter(lambda item: getattr(item.emotion, emotion) == _min, frames))
        max_second = max(max_frames, key=lambda x: x.frame.ts_second).frame.ts_second
        min_second = min(min_frames, key=lambda x: x.frame.ts_second).frame.ts_second
        tag_text = "%s increasing" % emotion
        if min_second > max_second:
            tag_text = "%s decreasing" % emotion
        change_duration = abs(min_second - max_second)
        change_amount = abs(_max - _min)
        if change_duration > 2 and change_amount > 20:
            add_twitch_clip_tag_request(clip_id, tag_text, change_amount, change_duration,
                                        min(min_second, max_second))
        max_frames.clear()
        min_frames.clear()
        happy.clear()

    def _calculate_happy(self, clip_id, max_happy_frames, min_happy_frames):
        max_happy_second = max(max_happy_frames, key=lambda x: x.frame.ts_second)
        min_happy_second = min(min_happy_frames, key=lambda x: x.frame.ts_second)
        happy_decreasing = False
        emotion = "Happy"
        tag_text = "%s Increasing" % emotion
        if min_happy_second > max_happy_second:
            happy_decreasing = True
            tag_text = "%s Decreasing" % emotion
        change_amount = abs(min_happy_second - max_happy_second)
        if change_amount > 1:
            add_twitch_clip_tag_request(clip_id, tag_text, change_amount, change_amount,
                                        min(min_happy_second, max_happy_second))

    def _scan_clip(self, scan_job_id: int, path: str, broadcaster: str, clip_id: int):

        with ClipVideoCapReader(broadcaster, clip_id) as reader:
            # size = len(reader_list)
            frame_number = 0
            seconds = get_length(path)
            size = reader.fps * seconds
            frames = []
            try:
                itr = reader.readYield(path)
                while True:
                    frame_list = self.scanned_frame(itr)
                    if len(frame_list) == 0:
                        break
                    self._frame_count += len(frame_list)
                    frame_number = frame_number + len(frame_list)
                    for frame in frame_list:
                        frames.append(frame)
                    if frame_number < size:
                        percent_done = frame_number / size
                    else:
                        percent_done = .99  # we guessed the fps wrong (ffmped)
                    i = int(percent_done * 100.0)
                    if i > 0 and i % 15 == 0:
                        update_scan_job_percent(scan_job_id, percent_done)
                return frames

            except BaseException as b:
                traceback.print_exc()
                pass

    def scanned_frame(self, itr):
        items = []
        try:
            frame = next(itr)
        except:

            return []

        last_second = -1
        if frame is not None:
            items.append(frame)
            last_second = frame.ts_second
        while frame is not None and len(items) < 10:
            if frame.ts_second == last_second:
                try:
                    frame = next(itr)
                except:
                    frame = None
                continue

            items.append(frame)
            last_second = frame.ts_second
            try:
                frame = next(itr)
            except:
                frame = None
            continue
        images = list(map(lambda x: x.image, items))

        results_list = DeepFace.analyze(images,
                                        actions=['emotion'],
                                        enforce_detection=False
                                        )

        item: DeepFaceResult
        index = 0
        scans = []
        for item in results_list:
            results_list[item]["frame"] = items[index]
            items[index].image = None
            result = DeepFaceResult(results_list[item])
            scans.append(result)
            # add_clip_twitch_tag_by_emotion(cl)
            index = index + 1
        return scans
