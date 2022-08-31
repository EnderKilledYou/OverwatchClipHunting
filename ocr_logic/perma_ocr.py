import random

from tesserocr import PyTessBaseAPI, PSM, OEM

from config.config import tess_fast_dir
from pipelines.queue_boss import QueueBossBase


class PermaOCR(QueueBossBase):
    def __init__(self):
        super().__init__()
        self.api = PyTessBaseAPI(path=tess_fast_dir, psm=PSM.SINGLE_COLUMN, oem=OEM.LSTM_ONLY)

    def __del__(self):
        super().__del__()
        self.api.Clear()
        self.api.ClearPersistentCache()
        self.api.End()

    def _process(self, image):
        self.api.SetImage(image)
        return self.api.GetUTF8Text()

    def GetUTF8Text(self, image, return_queue):
        self.add_work(image, return_queue)
        if return_queue is None:
            return None
        return return_queue.get()


perma_ocrs = [PermaOCR().start()] * 3

rand = random.Random()


def stop_all_ocr():
    for ocr in perma_ocrs:
        ocr.GetUTF8Text(None, None)
        ocr.stop()


def get_perma_ocr():
    index = rand.randint(0, len(perma_ocrs) - 1)
    return perma_ocrs[index]
