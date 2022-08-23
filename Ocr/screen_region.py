from PIL import Image
from tesserocr import PyTessBaseAPI

from Ocr.frames.frame import Frame
from Ocr.frames.frame_aggregator import FrameAggregator
from Ocr.frames.frame_tester import FrameTester
from Ocr.overwatch_readers.tesseract_instance import TesseractInstance


class ScreenRegion:
    def __del__(self):
        pass
    def crop(self, img):
        """crops this specific screen region."""
        pass

    def process(self, pil: Image, frame: Frame, frame_watcher: FrameAggregator, frame_tester: FrameTester,api: PyTessBaseAPI):
        """Runs the region analysis and return sends the result to the frame watcher."""
        pass
