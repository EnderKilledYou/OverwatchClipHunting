from PIL import Image
from pytesseract import image_to_string

from Ocr.frame import Frame
from Ocr.frame_aggregator import FrameAggregator
from Ocr.frame_tester import FrameTester
from Ocr.region_result import RegionResult
from Ocr.screen_region import ScreenRegion


class OverwatchSearchingForGameScreenRegion(ScreenRegion):
    def process(self, pil: Image, frame: Frame, frame_watcher: FrameAggregator, frame_tester: FrameTester,show:bool = False):
        top = self.crop(pil)
        text = image_to_string(top)
        text_stripped = text.strip()
        if len(text_stripped) == 0:
            return RegionResult(False, text,'nothing')
        if frame_tester.is_in_queue(text):
            frame_watcher.set_in_queue(frame)
            return RegionResult(True, text,'in_queue')
        if frame_tester.is_in_prepare_attack(text):
            frame_watcher.set_in_prepare(frame, 'attack')
            return RegionResult(True, text,'prepare_attack')
        if frame_tester.is_in_prepare_defense(text):
            frame_watcher.set_in_prepare(frame, 'defense')
            return RegionResult(True, text,'prepare_defense')
        return RegionResult(False, text,'nothing')

    def crop(self, img):
        right = img.width - (img.width * .35)
        left = (img.width * .35)
        upper = img.height / 2
        lower = img.height / 2
        im_crop = img.crop(  # (left, upper, right, lower)-
            (left,
             0,
             right,
             lower)
        )

        return im_crop