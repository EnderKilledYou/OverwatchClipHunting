import sys

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


class OverwatchScreenReader(ScreenReader):
    def __init__(self, framebuffer: VideoFrameBuffer ):
        from overwatch_events import overwatch_event
        super(OverwatchScreenReader, self).__init__(framebuffer)
        self.skip_frames = 0

        self.last_queue_check = 0
        self.frame_tester = FrameTester()
        self.Show = False
        self.last_action_second = 0
        self.ActionTextCropper = OverwatchActionScreenRegion()
        self.GameSearchCropper = OverwatchSearchingForGameScreenRegion()
        self.frame_watcher  = OrderedFrameAggregator(overwatch_event)

    def ocr(self, frame: Frame) -> None:
        if self.skip_frames > 0:
            print("skipping ")
            self.skip_frames = self.skip_frames - 1
            return
        try:
            img_grey = cv.cvtColor(frame.image, cv.COLOR_RGB2GRAY)
            # gray = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
            # ret2, th2 = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
            # dst = cv2.fastNlMeansDenoising(th2, 10, 10, 7)
            pil_grey = Image.fromarray(img_grey)
            # fromarray = Image.fromarray(frame.image)
            self.ActionTextCropper.process(pil_grey, frame, self.frame_watcher,
                                           self.frame_tester, self.Show)
            if not frame.empty:
                self.last_action_second = frame.ts_second
                return
            if self.last_queue_check != frame.ts_second and frame.ts_second % 30 == 0:
                self.last_queue_check = frame.ts_second
                self.GameSearchCropper.process(pil_grey, frame, self.frame_watcher,
                                               self.frame_tester, self.Show)
                if not frame.empty:
                    self.last_action_second = frame.ts_second
                if self.frame_watcher.in_queue:
                    print("In queue " + frame.source_name)
                    self.skip_frames += 2
                    return
                if frame.ts_second - self.last_action_second > 45 and frame.empty:
                    print("In queue or full screen " + frame.source_name)
                    self.skip_frames += 2

        except Exception as e:
            print(e, file=sys.stderr)
            import traceback
            traceback.print_exc()
