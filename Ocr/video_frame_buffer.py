from queue import Queue


class VideoFrameBuffer:
    Capturing: bool
    buffer: Queue
    _active: bool

    def __init__(self):
        self.Capturing = False
        self.buffer = Queue()
        self._active = True

    def buffer_broadcast(self):
        pass
    def stop(self):
        pass