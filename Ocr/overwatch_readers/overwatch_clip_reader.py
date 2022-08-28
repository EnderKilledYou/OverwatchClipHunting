import cv2 as cv
from PIL import Image
from tesserocr import PyTessBaseAPI

from Ocr.frames.frame import Frame
from Ocr.overwatch_readers.overwatch_action_screen_region import ClipActionTextCropper

from Ocr.screen_reader import ScreenReader



class OverwatchClipReader(ScreenReader):
    clip_id: int

    def __init__(self):
        super(OverwatchClipReader, self).__init__()



    def __del__(self):
        print(f"OverwatchClipReader Del")
        super().__del__()



    def ocr(self, frame: Frame, api: PyTessBaseAPI) -> None:
        img_grey = cv.cvtColor(frame.image, cv.COLOR_RGB2GRAY)
        pil_grey = Image.fromarray(img_grey)
        ClipActionTextCropper.process(pil_grey, frame, api)

        del frame
        frame = None
        pil_grey = None
        img_grey = None
