import cv2 as cv
from PIL import Image

from Ocr.frame import Frame
from Ocr.frame_aggregator import FrameAggregator
from Ocr.frame_tester import FrameTester
from Ocr.overwatch_action_screen_region import OverwatchActionScreenRegion
from Ocr.overwatch_searching_for_game_screen_region import OverwatchSearchingForGameScreenRegion
from Ocr.screen_reader import ScreenReader
from Ocr.video_frame_buffer import VideoFrameBuffer


class OverwatchScreenReader(ScreenReader):
    def __init__(self, framebuffer: VideoFrameBuffer, frame_watcher: FrameAggregator):
        super(OverwatchScreenReader, self).__init__(framebuffer)
        self.skip_frames = 0
        self.last_queue_check = 0
        self.frame_tester = FrameTester()
        self.Show = False
        self.ActionTextCropper = OverwatchActionScreenRegion()
        self.GameSearchCropper = OverwatchSearchingForGameScreenRegion()
        self.frame_watcher = frame_watcher

    def ocr(self, frame: Frame) -> None:
        if self.skip_frames > 0:
            self.skip_frames = self.skip_frames - 1
            return
        try:
            img_grey = cv.cvtColor(frame.image, cv.COLOR_RGB2GRAY)
            pil_grey = Image.fromarray(img_grey)
            # fromarray = Image.fromarray(frame.image)
            self.ActionTextCropper.process(pil_grey, frame, self.frame_watcher,
                                           self.frame_tester, self.Show)
            if frame.empty and (self.last_queue_check != frame.ts_second and frame.ts_second % 30 == 0):
                self.last_queue_check = frame.ts_second
                self.GameSearchCropper.process(pil_grey, frame, self.frame_watcher,
                                               self.frame_tester, self.Show)
                if self.frame_watcher.in_queue:
                    print("In queue " + frame.source_name)
                    self.skip_frames += 100

        except Exception as e:
            print(e)
            import traceback
            traceback.print_exc()
