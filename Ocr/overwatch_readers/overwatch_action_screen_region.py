import os
from queue import Queue

from PIL import Image

from tesserocr import PyTessBaseAPI

from Events.overwatch_clip_events import overwatch_clips_event
from Events.overwatch_events import overwatch_event
from Ocr.frames.frame import Frame
from Ocr.frames.frame_tester import FrameTester
from Ocr.frames.ordered_frame_aggregator import OrderedFrameAggregator
from Ocr.screen_region import ScreenRegion
from Ocr.wait_for_tess import wait_for_tess
from config.config import tess_fast_dir


class OverwatchActionScreenRegion(ScreenRegion):
    def __init__(self,events=overwatch_event):
        self.frame_watcher = OrderedFrameAggregator(events)
        self.frame_tester = FrameTester()
        self.return_queue = Queue()

    def __del__(self):
        del self.frame_watcher
        del self.frame_tester
        try:
            while True:
                self.return_queue.get(False)
        except:
            pass
        self.frame_watcher = None
        self.frame_tester = None
        self.return_queue = None

    def process(self, img: Image, frame: Frame, api: PyTessBaseAPI):

        if not os.path.exists(tess_fast_dir):
            wait_for_tess()

        img_crop = self.crop(img)
        # api.SetImage(img_crop)

        text = api.GetUTF8Text(img_crop, self.return_queue)

        img_crop = None

        frame.empty = True
        if len(text) < 4:
            text = None
            return
        frame_tester = self.frame_tester
        frame_watcher = self.frame_watcher

        if frame_tester.is_elimed_frame(text):
            frame_watcher.add_elimed_frame(frame)
            frame.empty = False
        if frame_tester.is_elim_frame(text):
            count = frame_tester.count_elim_frame(text)
            frame_watcher.add_elim_frame(frame, count)
            frame.empty = False

        if frame_tester.is_heal_frame(text):
            frame_watcher.add_healing_frame(frame)
            frame.empty = False

        if frame_tester.is_slept_frame(text):
            frame_watcher.add_slepting_frame(frame)
            frame.empty = False

        if frame_tester.is_assist_frame(text):
            frame_watcher.add_assist_frame(frame)
            frame.empty = False

        if frame_tester.is_blocking(text):
            frame_watcher.add_blocking_frame(frame)
            frame.empty = False

        if frame_tester.is_orb_gained(text):
            frame_watcher.add_orb_gained_frame(frame)
            frame.empty = False

        if frame_tester.is_defense(text):
            frame_watcher.add_defense_frame(frame)
            frame.empty = False

        if frame_tester.is_spawn_room_frame(text):
            frame_watcher.add_spawn_room_frame(frame)
            frame.empty = False
        text = None
        frame_tester = None
        frame_watcher = None

    def crop(self, img):
        right = img.width - (img.width * .25)
        left = (img.width * .27)
        upper = img.height / 2
        lower = img.height - (img.height * .18)
        im_crop = img.crop(  # (left, upper, right, lower)-
            (left,
             upper,  # crop the part where it tells you where shit happens.
             right,
             lower)
        )

        return im_crop

ClipActionTextCropper = OverwatchActionScreenRegion(events=overwatch_clips_event)
ActionTextCropper = OverwatchActionScreenRegion(events=overwatch_event)