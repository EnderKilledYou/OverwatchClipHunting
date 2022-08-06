from queue import Queue


class VideoFrameBuffer:
    Capturing = False
    buffer = Queue()
    Active = True
