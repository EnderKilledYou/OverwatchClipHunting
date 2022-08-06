import threading

from Ocr.frame import Frame
from Ocr.frame_aggregator import FrameAggregator


class OrderedFrameAggregator(FrameAggregator):
    lock = threading.Lock()

    def set_in_prepare(self, frame, mode):
        self.lock.acquire()
        try:
            super().set_in_prepare(frame, mode)
        except BaseException as be:
            raise
        finally:
            self.lock.release()

    def add_elim_frame(self, frame: Frame, elimination_appears_times: int):
        self.lock.acquire()
        try:
            super().add_elim_frame(frame, elimination_appears_times)
        except BaseException as be:
            raise
        finally:
            self.lock.release()

    def add_orb_gained_frame(self, frame):
        self.lock.acquire()
        try:
            super().add_orb_gained_frame(frame)
        except BaseException as be:
            raise
        finally:
            self.lock.release()

    def add_blocking_frame(self, frame):
        self.lock.acquire()
        try:
            super().add_blocking_frame(frame)
        except BaseException as be:
            raise
        finally:
            self.lock.release()

    def add_elimed_frame(self, frame):
        self.lock.acquire()
        try:
            super().add_elimed_frame(frame)
        except BaseException as be:
            raise
        finally:
            self.lock.release()

    def add_spawn_room_frame(self, frame):
        self.lock.acquire()
        try:
            super().add_spawn_room_frame(frame)
        except BaseException as be:
            raise
        finally:
            self.lock.release()

    def add_healing_frame(self, frame):
        self.lock.acquire()
        try:
            super().set_in_prepare(frame)
        except BaseException as be:
            raise
        finally:
            self.lock.release()

    def set_in_queue(self, frame):
        self.lock.acquire()
        try:
            super().set_in_prepare(frame)
        except BaseException as be:
            raise
        finally:
            self.lock.release()
