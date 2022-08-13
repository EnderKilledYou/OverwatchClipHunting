from queue import Queue


class VideoFrameBuffer:
    Capturing: bool
    buffer: Queue
    Active: bool

    def __init__(self):
        self.Capturing = False
        self.buffer = Queue()
        self.Active = True
