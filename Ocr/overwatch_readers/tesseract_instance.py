from PIL import Image
from tesserocr import PyTessBaseAPI

from config.config import tess_fast_dir


class TesseractInstance:
    _api: PyTessBaseAPI

    def __init__(self):
        self._api = PyTessBaseAPI(path=tess_fast_dir)

    def image_to_string(self, img: Image):
        self._api.SetImage(img)
        return self._api.GetUTF8Text()

    def __del__(self):
        print(f"TesseractInstance Del")
        self._api.End()
