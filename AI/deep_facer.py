import os

import sys
import traceback
from os.path import abspath
from threading import Timer
from typing import List

import cv2
import deepface.DeepFace
import numpy as np
from deepface import DeepFace
from deepface.DeepFace import build_model
from deepface.commons import functions
from keras.utils import image_utils

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
                with item:
                    pass

            frames.clear()
            update_scan_job_in_subclip(scan_job_id)
            Timer(8, clip_tag_to_clip, (clip_id, file, scan_job_id)).start()
            # update_scan_job_percent(scan_job_id, 1, True)



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

    
    def _scan_clip(self, scan_job_id: int, path: str, broadcaster: str, clip_id: int):

        with ClipVideoCapReader(broadcaster, clip_id) as reader:
            # size = len(reader_list)
            frame_number = 0
            seconds = get_length(path)
            size = reader.fps * seconds
            frames = []
            frame_list = []

            try:
                itr = reader.readYield(path)

                while True:
                    self.scanned_frame(itr, frame_list)
                    if len(frame_list) == 0:
                        break

                    self._frame_count += len(frame_list)
                    frame_number = frame_number + len(frame_list)
                    for frame in frame_list:
                        if 45 < frame.region.w < frame.frame_width * .9:
                            frames.append(frame)
                    frame_list.clear()
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

    
    def scanned_frame(self, itr, return_items):
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
        results = get_deep_results(items)
        for item in results:
            return_items.append(item)
        items.clear()
        return return_items


models = {}
models['emotion'] = build_model('Emotion')



def get_deep_result(frame):
    emotions = parse_emotions(frame.image)
    emotions["frame"] = frame
    frame.image = None
    return DeepFaceResult(emotions)



def get_deep_results(frames):
    emotions = []
    images = list(map(lambda x: x.image, frames))
    parse_emotions(images, emotions)
    for i in range(0, len(frames)):
        emotions[i]["frame"] = frames[i]
        emotions[i]['frame_width'] = frames[i].image.shape[0]
        emotions[i]['frame_height'] = frames[i].image.shape[1]
        frames[i].image = None
    images.clear()
    frames.clear()
    deeps = list(map(DeepFaceResult, emotions))
    emotions.clear()
    return deeps


emotion_labels = ['angry', 'disgust', 'fear', 'happy', 'sad', 'surprise', 'neutral']



def prep_images(numpy_image):
    return functions.preprocess_face(img=numpy_image, target_size=(48, 48), grayscale=True,
                                     enforce_detection=False, detector_backend='opencv',
                                     return_region=True)



def parse_emotions(numpy_images, items):
    prepped_images_and_regions = list(map(prep_images, numpy_images))
    prepped_images = map(lambda x: x[0], prepped_images_and_regions)
    # img, region = functions.preprocess_face(img=numpy_image, target_size=(48, 48), grayscale=True,
    #                                         enforce_detection=False, detector_backend='opencv',
    #                                         return_region=True)

    emotion_predictions = models['emotion'].predict(prepped_images, len(numpy_images), 2)  # [0, :]

    for i in range(len(numpy_images)):
        emotion_prediction = emotion_predictions[i]
        region = prepped_images_and_regions[i][1]
        sum_of_predictions = emotion_prediction.sum()
        resp_obj = {"region": region}
        resp_obj["emotion"] = {}

        for i in range(0, len(emotion_labels)):
            emotion_label = emotion_labels[i]
            emotion_prediction_val = 100 * emotion_prediction[i] / sum_of_predictions
            resp_obj["emotion"][emotion_label] = emotion_prediction_val

        resp_obj["dominant_emotion"] = emotion_labels[np.argmax(emotion_prediction)]
        items.append(resp_obj)
