from queue import Queue


class VideoFrameBuffer:
    Capturing: bool
    buffer: Queue
    _active: bool

    def get_one(self):
        return self.buffer.get(False)

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
