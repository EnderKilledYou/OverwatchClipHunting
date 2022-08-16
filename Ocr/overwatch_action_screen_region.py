import os

import cv2
import numpy
from PIL import Image
from pytesseract import image_to_string

from Ocr.frame import Frame
from Ocr.frame_aggregator import FrameAggregator
from Ocr.frame_tester import FrameTester
from Ocr.region_result import RegionResult
from Ocr.screen_region import ScreenRegion
from config.config import tess_fast_dir


class OverwatchActionScreenRegion(ScreenRegion):
    def process(self, pil: Image, frame: Frame, frame_watcher: FrameAggregator, frame_tester: FrameTester,
                show: bool = False):
        img_crop = self.crop(pil)
        text = image_to_string(img_crop,config=f'--tessdata-dir "{tess_fast_dir}"',lang='eng')  # , lang='eng')
        frame.empty = True
        if len(text) < 4:
            return
        if frame_tester.is_first_menu_frame(text):
            return  # later

        if frame_tester.is_elimed_frame(text):
            frame_watcher.add_elimed_frame(frame)
            frame.empty = False
        if frame_tester.is_elim_frame(text):
            count = frame_tester.count_elim_frame(text)
            frame_watcher.add_elim_frame(frame, count)
            frame.empty = False

        if frame_tester.is_heal_frame(text):
            frame_watcher.add_healing_frame(frame)
            frame.empty = False

        if frame_tester.is_slept_frame(text):
            frame_watcher.add_slepting_frame(frame)
            frame.empty = False

        if frame_tester.is_assist_frame(text):
            frame_watcher.add_assist_frame(frame)
            frame.empty = False

        if frame_tester.is_blocking(text):
            frame_watcher.add_blocking_frame(frame)
            frame.empty = False

        if frame_tester.is_orb_gained(text):
            frame_watcher.add_orb_gained_frame(frame)
            frame.empty = False

        if frame_tester.is_defense(text):
            frame_watcher.add_defense_frame(frame)
            frame.empty = False

        if frame_tester.is_spawn_room_frame(text):
            frame_watcher.add_spawn_room_frame(frame)
            frame.empty = False

    def crop(self, img):
        right = img.width - (img.width * .25)
        left = (img.width * .27)
        upper = img.height / 2
        lower = img.height - (img.height * .18)
        im_crop = img.crop(  # (left, upper, right, lower)-
            (left,
             upper,  # crop the part where it tells you where shit happens.
             right,
             lower)
        )

        return im_crop
