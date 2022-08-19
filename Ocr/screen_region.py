from PIL import Image

from Ocr.frames.frame import Frame
from Ocr.frames.frame_aggregator import FrameAggregator
from Ocr.frames.frame_tester import FrameTester


class ScreenRegion:
    def crop(self, img):
        """crops this specific screen region."""
        pass

    def process(self, pil: Image, frame: Frame, frame_watcher: FrameAggregator, frame_tester: FrameTester,
                show: bool = False):
        """Runs the region analysis and return sends the result to the frame watcher."""
        pass
