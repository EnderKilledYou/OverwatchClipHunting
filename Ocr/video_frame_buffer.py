from queue import Queue


class VideoFrameBuffer:
    Capturing: bool
    buffer: Queue
    _active: bool
    def get_queue_size(self):
        if self.reader is None:
            return 0
    def get_one(self):
        return self.buffer.get(False)
    def __init__(self):
        self.Capturing = False
        self.buffer = Queue()
        self._active = True

    def buffer_broadcast(self):
        pass
    def stop(self):
        pass