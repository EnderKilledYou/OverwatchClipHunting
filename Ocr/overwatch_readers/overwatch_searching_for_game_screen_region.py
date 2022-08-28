import os


from PIL import Image
from pytesseract import image_to_string
from tesserocr import PyTessBaseAPI

import ocr_logic.crop_center
from Ocr.frames.frame import Frame
from Ocr.frames.frame_aggregator import FrameAggregator
from Ocr.frames.frame_tester import FrameTester
from Ocr.overwatch_readers.tesseract_instance import TesseractInstance
from Ocr.wait_for_tess import wait_for_tess
from Ocr.screen_region import ScreenRegion
from config.config import tess_fast_dir


class OverwatchSearchingForGameScreenRegion(ScreenRegion):

    def process(self, pil: Image, frame: Frame, frame_watcher: FrameAggregator, frame_tester: FrameTester,
                api: PyTessBaseAPI):

        top = self.crop(pil)
        if not os.path.exists(tess_fast_dir):
            wait_for_tess()
        api.SetImage(top)
        text = api.GetUTF8Text()
        text_stripped = text.strip()
        if len(text_stripped) == 0:
            return
        if frame_tester.is_in_queue(text_stripped):
            frame.empty = False
            frame_watcher.set_in_queue(frame)
            return

        if frame_tester.is_in_prepare_attack(text_stripped):
            frame.empty = False
            frame_watcher.set_in_prepare(frame, 'attack')
            return
        if frame_tester.is_in_escort(text_stripped):
            frame.empty = False
            frame_watcher.add_escort_frame(frame)

        if frame_tester.is_in_contested(text_stripped):
            frame.empty = False
            frame_watcher.add_contested_frame(frame)

        if frame_tester.is_in_prepare_defense(text_stripped):
            frame.empty = False
            frame_watcher.set_in_prepare(frame, 'defense')

        # return RegionResult(True, text,'prepare_defense')
        return  # RegionResult(False, text,'nothing')

    def crop(self, img):
        right = img.width - (img.width * .35)
        left = 0

        lower = img.height / 2
        im_crop = ocr_logic.crop_center.crop(  # (left, upper, right, lower)-
            (left,
             0,
             right,
             lower)
        )

        return im_crop
