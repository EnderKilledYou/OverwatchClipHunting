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


class OverwatchActionScreenRegion(ScreenRegion):
    def process(self, pil: Image, frame: Frame, frame_watcher: FrameAggregator, frame_tester: FrameTester,
                show: bool = False):
        img_crop = self.crop(pil)
        text = image_to_string(img_crop).strip()  # , lang='eng')


        if len(text) < 4:
            return# RegionResult(False, text, 'nothing')
        if frame_tester.is_first_menu_frame(text):
            return# RegionResult(True, text, 'menu_1')
        if frame_tester.is_elimed_frame(text):
            frame_watcher.add_elimed_frame(frame)
            return# RegionResult(True, text, 'elimed')

        if frame_tester.is_elim_frame(text):
            count = frame_tester.count_elim_frame(text)
            frame_watcher.add_elim_frame(frame, count)
            return# RegionResult(True, text, 'elim')

        if frame_tester.is_blocking(text):
            return# RegionResult(True, text, 'blocking')

        if frame_tester.is_heal_frame(text):
            frame_watcher.add_healing_frame(frame)
            return# RegionResult(True, text, 'heal')

        if frame_tester.is_orb_gained(text):
            # frame_watcher.add_healing_frame(frame)
            return# RegionResult(True, text, 'orb')

        if frame_tester.is_defense(text):
            # frame_watcher.add_healing_frame(frame)
            return# RegionResult(True, text, 'defense')

        if frame_tester.is_spawn_room_frame(text):
            frame_watcher.add_spawn_room_frame(frame)
            return# RegionResult(True, text, 'spawn_room')



        return# RegionResult(False, text, 'nothing')

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
