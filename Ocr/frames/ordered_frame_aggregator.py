
import threading

from Ocr.frames.frame import Frame
from Ocr.frames.frame_aggregator import FrameAggregator


class OrderedFrameAggregator(FrameAggregator):
    def __init__(self, ee):
        super(OrderedFrameAggregator, self).__init__(ee)
        self.lock = threading.Lock()

    def __del__(self):
        self.emitter = None
        if hasattr(self, 'lock'):
            del self.lock
            self.lock = None

    
    def set_in_prepare(self, frame, mode):
        self.lock.acquire()
        try:
            super().set_in_prepare(frame, mode)
        except BaseException as be:
            raise
        finally:
            self.lock.release()

    
    def add_assist_frame(self, frame):
        self.lock.acquire()
        try:
            super().add_assist_frame(frame)
        except BaseException as be:
            raise
        finally:
            self.lock.release()

    
    def add_escort_frame(self, frame):
        self.lock.acquire()
        try:
            super().add_escort_frame(frame)
        except BaseException as be:
            raise
        finally:
            self.lock.release()

    
    def add_contested_frame(self, frame):
        self.lock.acquire()
        try:
            super().add_contested_frame(frame)
        except BaseException as be:
            raise
        finally:
            self.lock.release()

    
    def add_defense_frame(self, frame):
        self.lock.acquire()
        try:
            super().add_defense_frame(frame)
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
            super().add_healing_frame(frame)
        except BaseException as be:
            raise
        finally:
            self.lock.release()

    
    def add_slepting_frame(self, frame):
        self.lock.acquire()
        try:
            super().add_slepting_frame(frame)
        except BaseException as be:
            raise
        finally:
            self.lock.release()

    
    def set_in_queue(self, frame):
        self.lock.acquire()
        try:
            super().set_in_queue(frame)
        except BaseException as be:
            raise
        finally:
            self.lock.release()
