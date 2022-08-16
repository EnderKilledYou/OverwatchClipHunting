from PIL import Image
from pytesseract import image_to_string

from Ocr.frame import Frame
from Ocr.frame_aggregator import FrameAggregator
from Ocr.frame_tester import FrameTester
from Ocr.region_result import RegionResult
from Ocr.screen_region import ScreenRegion
from config.config import tess_fast_dir


class OverwatchSearchingForGameScreenRegion(ScreenRegion):
    def process(self, pil: Image, frame: Frame, frame_watcher: FrameAggregator, frame_tester: FrameTester,
                show: bool = False):

        top = self.crop(pil)
        text = image_to_string(top,config=f'--tessdata-dir "{tess_fast_dir}"',lang='eng')
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
        upper = img.height / 2
        lower = img.height / 2
        im_crop = img.crop(  # (left, upper, right, lower)-
            (left,
             0,
             right,
             lower)
        )

        return im_crop
