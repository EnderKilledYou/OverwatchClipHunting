import sys
from time import sleep

import cv2 as cv
from PIL import Image
from tesserocr import PyTessBaseAPI

from Ocr.frames.frame import Frame
from Ocr.frames.frame_tester import FrameTester
from Ocr.frames.ordered_frame_aggregator import OrderedFrameAggregator
from Ocr.overwatch_readers.overwatch_action_screen_region import OverwatchActionScreenRegion, ActionTextCropper
from Ocr.overwatch_readers.overwatch_searching_for_game_screen_region import OverwatchSearchingForGameScreenRegion
from Ocr.overwatch_readers.tesseract_instance import TesseractInstance
from Ocr.screen_reader import ScreenReader
from Ocr.video_frame_buffer import VideoFrameBuffer
from cloud_logger import cloud_error_logger

from Events.overwatch_events import overwatch_event


class OverwatchScreenReader(ScreenReader):
    def __del__(self):
        super().__del__()
        print(f"OverwatchScreenReader Del")
        if hasattr(self, 'frame_tester'):
            del self.frame_tester

        if hasattr(self, 'GameSearchCropper'):
            del self.GameSearchCropper
        if hasattr(self, 'frame_watcher'):
            del self.frame_watcher

    def __init__(self):

        super(OverwatchScreenReader, self).__init__()
        self.skip_frames = 0

        self.last_queue_check = 0
        self.frame_tester = FrameTester()
        self.Show = False
        self.last_action_second = 0

        self.GameSearchCropper = OverwatchSearchingForGameScreenRegion()
        self.frame_watcher = OrderedFrameAggregator(overwatch_event)

    def ocr(self, frame: Frame, api: PyTessBaseAPI) -> None:

        try:
            # img_grey = cv.cvtColor(frame.image, cv.COLOR_RGB2GRAY)
            # pil_grey = Image.fromarray(img_grey)
            pil_grey = Image.fromarray(frame.image)
            if frame.frame_number % 100 == 0:
                print(f"Processing frame {frame.frame_number} for {frame.source_name}")
            ActionTextCropper.process(pil_grey, frame, self.frame_watcher,
                                      self.frame_tester, api)
            #del img_grey
            del pil_grey
            if frame.empty:
                del frame



        except BaseException as e:
            cloud_error_logger(e, file=sys.stderr)
            import traceback
            traceback.print_exc()
