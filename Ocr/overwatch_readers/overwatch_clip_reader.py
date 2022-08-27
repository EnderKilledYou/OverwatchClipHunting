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
        super(OverwatchClipReader, self).__init__()

        self.ActionTextCropper = OverwatchActionScreenRegion(events=overwatch_clips_event)

    def __del__(self):
        print(f"OverwatchClipReader Del")
        super().__del__()

        if hasattr(self, 'ActionTextCropper'):
            del self.ActionTextCropper

    def ocr(self, frame: Frame, api: PyTessBaseAPI) -> None:
        img_grey = cv.cvtColor(frame.image, cv.COLOR_RGB2GRAY)
        pil_grey = Image.fromarray(img_grey)
        self.ActionTextCropper.process(pil_grey, frame, api)

        del frame
        frame = None
        pil_grey = None
        img_grey = None
