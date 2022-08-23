import threading
from queue import Queue
from time import sleep

import cv2
import cv2 as cv

import cloud_logger
from Ocr.frames.frame import Frame
from Ocr.no_stream_error import NoStreamError
from config.config import sample_frame_rate


class StreamEndedError(BaseException):
    pass


class VideoCapReader:
    def __init__(self, streamer_name):
        self._count_lock = threading.Lock()
        self.Active = False
        self.streamer_name = streamer_name
        self.sample_every_count = 30
        self.items_read = 0
        self.items_drained = 0
        self.fps = 1

    def count(self):
        try:
            self._count_lock.acquire()
            return self.items_read - self.items_drained
        finally:
            self._count_lock.release()
            pass

    def incr_items_drained(self):
        try:
            self._count_lock.acquire()
            self.items_drained = self.items_drained + 1
        finally:
            self._count_lock.release()
            pass

    def incr_items_read(self):
        try:
            self._count_lock.acquire()
            self.items_read = self.items_read + 1
        finally:
            self._count_lock.release()
            pass

    def _read_one(self, frame_number, fps, loose_buffer=False):
        ret, frame = self.video_capture.read()
        if not ret:
            raise StreamEndedError("Could not read frame")

        if frame_number % self.sample_every_count == 0:
            if not loose_buffer and self.count() > 50:
                return None
            return Frame(frame_number, frame, frame_number // fps, self.streamer_name)
        return None

    def read(self, url, buffer):
        self.Active = True
        self._acquire(url)
        try:
            self._read(buffer)
        except StreamEndedError:
            pass
        self._release()

    def readYield(self, url):
        self.Active = True
        self._acquire(url)
        try:
            video_capture = self.video_capture

            fps = int(video_capture.get(cv.CAP_PROP_FPS))
            if fps > 500:
                fps = 60
            if fps < 10:
                fps = 60
            self.fps = fps
            self.sample_every_count = fps // sample_frame_rate
            for frame in self._yield_frames(fps,True):
                yield frame
        except StreamEndedError:
            try:
                self._release()
            except:
                pass
            pass

    def stop(self):
        self.Active = False

    def _read(self, buffer: Queue):

        fps = int(self.video_capture.get(cv.CAP_PROP_FPS))
        if fps > 500:
            fps = 60
        if fps < 10:
            fps = 60
        self.fps = fps
        frame_number = 0

        self.sample_every_count = fps // sample_frame_rate
        cloud_logger.cloud_message(
            f"Starting sampling.. sampling {fps} /  {sample_frame_rate} = {self.sample_every_count}")
        while self.Active and self._next_frame(frame_number, buffer):
            frame_number = frame_number + 1

    def _next_frame(self, frame_number, buffer: Queue):
        item = self._read_one(frame_number, self.fps)

        if item is None:
            return True

        buffer.put(item)

        self.incr_items_read()
        return True

    def _yield_frames(self, fps, loose_buffer=False):
        frame_number = 0
        while self.Active:
            item = self._read_one(frame_number, fps, loose_buffer)
            if item is None:
                break

            if frame_number % self.sample_every_count == 0:
                yield item
                self.incr_items_read()
            frame_number = frame_number + 1

    def _acquire(self, url: str):
        self.video_capture = cv2.VideoCapture(url)
        self.video_capture.set(cv2.CAP_PROP_BUFFERSIZE, 2)
        if not self.video_capture:
            raise NoStreamError("Capture could not open stream")
        if not self.video_capture.isOpened():
            self.video_capture.open(url)

    def _release(self):
        if not self.video_capture:
            return
        self.video_capture.release()
        self.video_capture = None


class ClipVideoCapReader(VideoCapReader):
    def __init__(self, streamer_name: str, clip_id: int):
        super(ClipVideoCapReader, self).__init__(streamer_name)
        self.clip_id = clip_id
        self.sample_every_count = 30

    def _read_one(self, frame_number, fps,loose_buffer=False):
        ret, frame = self.video_capture.read()
        if not ret:
            raise StreamEndedError("Could not read frame")
        return Frame(frame_number, frame, frame_number // fps, self.streamer_name, self.clip_id)
