import cv2 as cv
from PIL import Image
from pyee import EventEmitter

from Ocr.frame import Frame
from Ocr.frame_tester import FrameTester
from Ocr.ordered_frame_aggregator import OrderedFrameAggregator
from Ocr.overwatch_action_screen_region import OverwatchActionScreenRegion
from Ocr.screen_reader import ScreenReader
from overwatch_clip_events import overwatch_clips_event


class OverwatchClipReader(ScreenReader):
    clip_id: int

    def __init__(self):
        super(OverwatchClipReader, self).__init__(None)
        self.frame_tester = FrameTester()
        self.ActionTextCropper = OverwatchActionScreenRegion()
        self.frame_watcher = OrderedFrameAggregator(overwatch_clips_event)

    def ocr(self, frame: Frame) -> None:
        img_grey = cv.cvtColor(frame.image, cv.COLOR_RGB2GRAY)
        pil_grey = Image.fromarray(img_grey)
        self.ActionTextCropper.process(pil_grey, frame, self.frame_watcher,
                                       self.frame_tester)
