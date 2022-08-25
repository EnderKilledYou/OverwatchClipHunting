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
        self.video_capture = None
        self.error_count = 0

    def __del__(self):
        print(f"VideoCapReader Del")
        self._count_lock = None
        if hasattr(self, 'video_capture') and self.video_capture is not None:
            self._release()
            del self.video_capture

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

    def _read_one(self, frame_number, fps):

        ret, frame = self.video_capture.read()
        if not ret:
            raise StreamEndedError("Could not read frame")

        if frame_number % self.sample_every_count == 0:
            return Frame(frame_number, frame, frame_number // fps, self.streamer_name)
        del frame
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

            fps = int(self.video_capture.get(cv.CAP_PROP_FPS))
            if fps > 500:
                fps = 60
            if fps < 10:
                fps = 60
            self.fps = fps
            self.sample_every_count = fps // sample_frame_rate
            return self._yield_frames(fps)
        except StreamEndedError:
            try:
                self._release()
            except:
                pass
            pass

    def stop(self):
        self.Active = False
        self._release()

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
        if self.count() > 150:
            print(f"transfer full, waiting {self.streamer_name}")
            sleep(1)
            return True
        item = self._read_one(frame_number, self.fps)
        if item is None:
            return True

        if frame_number > 0 and frame_number % 10 == 0 and self.count() == 0:
            print(f"Sleeping off empty buffer {self.streamer_name}")
            sleep(1)  # let the video cap have some time to buffer
        buffer.put(item)

        self.incr_items_read()
        return True

    def _yield_frames(self, fps):
        frame_number = 0
        while self.Active:
            try:
                item = self._read_one(frame_number, fps)
            except StreamEndedError:
                break
            if item is None:
                break

            yield item
            self.incr_items_read()

            frame_number = frame_number + 1

    def _acquire(self, url: str):
        self.video_capture = cv2.VideoCapture(url, apiPreference=cv2.CAP_IMAGES)
        self.video_capture.set(cv2.CAP_PROP_BUFFERSIZE, 2)
        if not self.video_capture:
            raise NoStreamError("Capture could not open stream")
        if not self.video_capture.isOpened():
            self.video_capture.open(url)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self._release()

    def _release(self):
        if self.video_capture is None:
            return
        self.video_capture.release()
        self.video_capture = None


class ClipVideoCapReader(VideoCapReader):
    def __init__(self, streamer_name: str, clip_id: int):
        super(ClipVideoCapReader, self).__init__(streamer_name)
        self.clip_id = clip_id
        self.sample_every_count = 30

