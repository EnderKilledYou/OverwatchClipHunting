from PIL import Image
from tesserocr import PyTessBaseAPI

from Ocr.frames.frame import Frame
from Ocr.frames.frame_aggregator import FrameAggregator
from Ocr.frames.frame_tester import FrameTester
from Ocr.overwatch_readers.tesseract_instance import TesseractInstance


class ScreenRegion:
    def __del__(self):
        print(f"ScreenRegion Del")
        pass

    def __del__(self):
        print(f"ScreenRegion Del")
        pass

    def crop(self, img):
        """crops this specific screen region."""
        pass

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        del self

    def process(self, pil: Image, frame: Frame, api: PyTessBaseAPI):
        """Runs the region analysis and return sends the result to the frame watcher."""
        pass
