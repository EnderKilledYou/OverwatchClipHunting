import random
import threading
from queue import Queue

from tesserocr import PyTessBaseAPI, PSM, OEM

from config.config import tess_fast_dir


class PermaOCR:
    def __init__(self):
        self.api = PyTessBaseAPI(path=tess_fast_dir, psm=PSM.SPARSE_TEXT, oem=OEM.LSTM_ONLY)
        self.queue = Queue()

    def __del__(self):
        self.api.Clear()
        self.api.ClearPersistentCache()
        self.api.End()

    def start(self, ):
        threading.Thread(target=self._loop).start()
        return self

    def _loop(self):
        while (True):
            work = self.queue.get()
            image, return_queue = work
            self.api.SetImage(image)
            return_queue.put(self.api.GetUTF8Text())
            image = None
            return_queue = None

    def GetUTF8Text(self, image, return_queue):
        self.queue.put((image, return_queue))
        return return_queue.get()


perma_ocrs = [PermaOCR().start(), PermaOCR().start(), PermaOCR().start()]
rand = random.Random()


def get_perma_ocr():
    index = rand.randint(0, len(perma_ocrs) - 1)
    return perma_ocrs[index]
