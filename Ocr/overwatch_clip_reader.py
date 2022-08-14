import cv2 as cv
from PIL import Image
from pyee import EventEmitter

from Ocr.frame import Frame
from Ocr.frame_aggregator import FrameAggregator
from Ocr.frame_tester import FrameTester
from Ocr.ordered_frame_aggregator import OrderedFrameAggregator
from Ocr.overwatch_action_screen_region import OverwatchActionScreenRegion
from Ocr.overwatch_searching_for_game_screen_region import OverwatchSearchingForGameScreenRegion
from Ocr.screen_reader import ScreenReader
from Ocr.video_frame_buffer import VideoFrameBuffer
from overwatch_clip_events import overwatch_clips_event

from overwatch_events import overwatch_event


class OverwatchClipReader(ScreenReader):
    clip_id: int

    def __init__(self ):
        super(OverwatchClipReader, self).__init__(None)

        self.frame_tester = FrameTester()
        self.ActionTextCropper = OverwatchActionScreenRegion()
        self.frame_watcher = OrderedFrameAggregator(overwatch_clips_event )

    def ocr(self, frame: Frame) -> None:
        img_grey = cv.cvtColor(frame.image, cv.COLOR_RGB2GRAY)
        # gray = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
        # ret2, th2 = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        # dst = cv2.fastNlMeansDenoising(th2, 10, 10, 7)
        pil_grey = Image.fromarray(img_grey)
        # fromarray = Image.fromarray(frame.image)
        self.ActionTextCropper.process(pil_grey, frame, self.frame_watcher,
                                       self.frame_tester)
