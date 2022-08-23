from queue import Queue


class VideoFrameBuffer:
    Capturing: bool
    buffer: Queue
    _active: bool

    def get_one(self):
        return self.buffer.get(False)

    def __del__(self):
        self.buffer = None
        del self.buffer

    def __init__(self):
        self.reader = None
        self.Capturing = False
        self.buffer = Queue()
        self._active = True

    def buffer_broadcast(self):
        pass

    def stop(self):
        pass

    @property
    def active(self):
        return self._active

    def is_empty(self):
        return self.buffer.qsize() == 0
