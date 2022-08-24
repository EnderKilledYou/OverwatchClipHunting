import cv2 as cv
from PIL import Image
from tesserocr import PyTessBaseAPI

from Ocr.frames.frame import Frame
from Ocr.frames.frame_tester import FrameTester
from Ocr.frames.ordered_frame_aggregator import OrderedFrameAggregator
from Ocr.overwatch_readers.overwatch_action_screen_region import OverwatchActionScreenRegion
from Ocr.overwatch_readers.tesseract_instance import TesseractInstance
from Ocr.screen_reader import ScreenReader
from Events.overwatch_clip_events import overwatch_clips_event


class OverwatchClipReader(ScreenReader):
    clip_id: int

    def __init__(self):
        super(OverwatchClipReader, self).__init__(None)
        self.frame_tester = FrameTester()
        self.ActionTextCropper = OverwatchActionScreenRegion()
        self.frame_watcher = OrderedFrameAggregator(overwatch_clips_event)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.__del__()

    def __del__(self):
        super().__del__()
        if hasattr(self, 'frame_tester'):
            del self.frame_tester
        if hasattr(self, 'ActionTextCropper'):
            del self.ActionTextCropper
        if hasattr(self, 'frame_watcher'):
            del self.frame_watcher

    def ocr(self, frame: Frame, api: PyTessBaseAPI) -> None:
        img_grey = cv.cvtColor(frame.image, cv.COLOR_RGB2GRAY)
        pil_grey = Image.fromarray(img_grey)
        self.ActionTextCropper.process(pil_grey, frame, self.frame_watcher,
                                       self.frame_tester, api)
