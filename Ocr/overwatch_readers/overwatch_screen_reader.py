import sys

import cv2 as cv
from PIL import Image
from tesserocr import PyTessBaseAPI

from Ocr.frames.frame import Frame
from Ocr.frames.frame_tester import FrameTester
from Ocr.frames.ordered_frame_aggregator import OrderedFrameAggregator
from Ocr.overwatch_readers.overwatch_action_screen_region import OverwatchActionScreenRegion
from Ocr.overwatch_readers.overwatch_searching_for_game_screen_region import OverwatchSearchingForGameScreenRegion
from Ocr.overwatch_readers.tesseract_instance import TesseractInstance
from Ocr.screen_reader import ScreenReader
from Ocr.video_frame_buffer import VideoFrameBuffer
from cloud_logger import cloud_error_logger


class OverwatchScreenReader(ScreenReader):
    def __init__(self, framebuffer: VideoFrameBuffer):
        from Events.overwatch_events import overwatch_event
        super(OverwatchScreenReader, self).__init__(framebuffer)
        self.skip_frames = 0

        self.last_queue_check = 0
        self.frame_tester = FrameTester()
        self.Show = False
        self.last_action_second = 0
        self.ActionTextCropper = OverwatchActionScreenRegion()
        self.GameSearchCropper = OverwatchSearchingForGameScreenRegion()
        self.frame_watcher = OrderedFrameAggregator(overwatch_event)

    def ocr(self, frame: Frame,api : PyTessBaseAPI) -> None:
        if self.skip_frames > 0:
            print("skipping ")
            self.skip_frames = self.skip_frames - 1
            return
        try:
            img_grey = cv.cvtColor(frame.image, cv.COLOR_RGB2GRAY)
            pil_grey = Image.fromarray(img_grey)

            self.ActionTextCropper.process(pil_grey, frame, self.frame_watcher,
                                           self.frame_tester,api)
            if not frame.empty:
                self.last_action_second = frame.ts_second
                return
            if self.last_queue_check != frame.ts_second and frame.ts_second % 30 == 0:
                self.last_queue_check = frame.ts_second
                self.GameSearchCropper.process(pil_grey, frame, self.frame_watcher,
                                               self.frame_tester, api)
                if not frame.empty:
                    self.last_action_second = frame.ts_second
                if self.frame_watcher.in_queue:
                    import start_up_flask
                    print("In queue " + frame.source_name)
                    start_up_flask.alli.stop_streamer(frame.source_name)
                    self.skip_frames += 2
                    return
                if frame.ts_second - self.last_action_second > 45 and frame.empty:
                    print("In queue or full screen " + frame.source_name)
                    self.skip_frames += 2

        except Exception as e:
            cloud_error_logger(e, file=sys.stderr)
            import traceback
            traceback.print_exc()
