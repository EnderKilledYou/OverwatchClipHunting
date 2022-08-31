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
        self._lock = threading.Lock()
        self._queue_size = 0

    def count(self):
        return self._queue_size

    def _decr_work(self):
        try:
            self._lock.acquire()
            self._queue_size = self._queue_size - 1
        except:
            pass
        finally:
            self._lock.release()

    def _incr_work(self):
        try:
            self._lock.acquire()
            self._queue_size = self._queue_size + 1
        except:
            pass
        finally:
            self._lock.release()

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
                    self._decr_work()
                continue
            self.api.SetImage(image)
            return_queue.put(self.api.GetUTF8Text())
            self._decr_work()
            image = None
            return_queue = None

    def GetUTF8Text(self, image, return_queue):
        self._incr_work()
        self.queue.put((image, return_queue))
        if return_queue is None:
            return None
        return return_queue.get()


perma_ocrs = [PermaOCR().start()]


def stop_all_ocr():
    for ocr in perma_ocrs:
        ocr.GetUTF8Text(None, None)
        ocr.stop()


def get_perma_ocr():
    return min(*perma_ocrs, key=lambda x: x.count())
