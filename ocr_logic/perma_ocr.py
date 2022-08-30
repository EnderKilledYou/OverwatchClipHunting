import random
import threading
from queue import Queue

import cancel_token
from cancel_token import CancellationToken
from tesserocr import PyTessBaseAPI, PSM, OEM

from config.config import tess_fast_dir


class PermaOCR:
    def __init__(self):
        self.api = PyTessBaseAPI(path=tess_fast_dir, psm=PSM.SINGLE_COLUMN, oem=OEM.LSTM_ONLY)
        self.queue = Queue()
        self._token = CancellationToken()

    def stop(self):
        self._token.cancel()

    def __del__(self):
        self.api.Clear()
        self.api.ClearPersistentCache()
        self.api.End()

    def start(self, ):
        threading.Thread(target=self._loop).start()
        return self

    def _loop(self):
        while not self._token.cancelled:
            work = self.queue.get()
            image, return_queue = work
            if image is None:
                if return_queue is not None:
                    return_queue.put(None)
                continue
            self.api.SetImage(image)
            return_queue.put(self.api.GetUTF8Text())
            image = None
            return_queue = None

    def GetUTF8Text(self, image, return_queue):
        self.queue.put((image, return_queue))
        if return_queue is None:
            return None
        return return_queue.get()


perma_ocrs = [PermaOCR().start(), PermaOCR().start(), PermaOCR().start()]
rand = random.Random()


def stop_all_ocr():
    for ocr in perma_ocrs:
        ocr.GetUTF8Text(None, None)
        ocr.stop()


ocr_lock = threading.Lock()
ocr_settings = {'ocr_index': 0}


def get_perma_ocr():
    try:
        ocr_lock.acquire()
        ocr = perma_ocrs[ocr_settings['ocr_index']]
        if ocr_settings['ocr_index'] + 1 >= len(perma_ocrs):
            ocr_settings['ocr_index'] = 0
        else:
            ocr_settings['ocr_index'] = ocr_settings['ocr_index'] + 1
        return ocr
    except:
        pass
    finally:
        ocr_lock.release()
