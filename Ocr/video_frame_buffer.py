from queue import Queue


class VideoFrameBuffer:
    Capturing: bool
    buffer: Queue
    _active: bool

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.__del__()

    def get_one(self):
        return self.buffer.get(False)

    def __del__(self):
        while True:
            try:
                buffer_get = self.buffer.get(False)
                del buffer_get
            except:
                pass
        del self.buffer
        self.buffer = None

    def __init__(self):
        self.reader = None
        self.Capturing = False
        self.buffer = Queue()
        self._active = True

    def get_stats(self):
        qsize = self.count()
        frames_pending = qsize * self.sample_every_count
        frames_finished = self.items_drained * self.sample_every_count
        back_fill_seconds = frames_pending // self.fps
        return qsize, frames_finished, frames_finished, back_fill_seconds, self.fps, self.sample_every_count, self.items_read

    def buffer_broadcast(self):
        pass

    def stop(self):
        pass

    @property
    def active(self):
        return self._active

    def is_empty(self):
        return self.buffer.qsize() == 0
