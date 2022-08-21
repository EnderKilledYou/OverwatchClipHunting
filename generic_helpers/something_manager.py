import sys
import threading
from queue import Queue, Empty
from time import sleep

from cloud_logger import cloud_error_logger


class ThreadedManager:
    max_threads: int

    def __init__(self, max_threads=2, exit_on_empty=False):
        self._exit_on_empty = exit_on_empty
        self.max_threads = max_threads
        self.buffer = Queue()
        self._active = True
        self._threads = []

    def start(self):
        for i in range(0, self.max_threads):
            _thread = threading.Thread(target=self._start)
            _thread.start()
            self._threads.append(_thread)

    def join(self, timeout=None):
        for thread in self._threads:
            thread.join(timeout)

    def stop(self):
        self._active = False
        self._stop()

    def _stop(self):
        pass

    def add_job(self, scan_job):

        self.buffer.put(scan_job)

    def _do_work(self, item):
        pass

    def _repeat(self):
        if not self._active:
            return
        try:
            job = self.buffer.get(False)
            self._do_work(job)
        except Empty:
            if self._exit_on_empty:
                return
        except BaseException as b:
            cloud_error_logger(b, file=sys.stderr)
        finally:
            _thread = threading.Timer(2, self._start)
            _thread.start()

    def _start(self):
        while self._active:
            try:
                job = self.buffer.get(False)
                self._do_work(job)
            except Empty:

                if self._exit_on_empty:
                    return
                sleep(5)
            except BaseException as b:
                cloud_error_logger(b, file=sys.stderr)

            finally:
                pass
