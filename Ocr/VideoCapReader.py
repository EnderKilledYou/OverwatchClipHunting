import traceback
from queue import Queue

import cv2
import cv2 as cv

from Ocr.frame import Frame
from Ocr.no_stream_error import NoStreamError


class StreamEndedError(BaseException):
    pass


class VideoCapReader:
    def __init__(self, streamer_name):

        self.Active = False
        self.streamer_name = streamer_name
        self.sample_every_count = 30
        self.items_read = 0
        self.items_drained = 0

    def incr_items_drained(self):
        self.items_drained = self.items_drained + 1

    def _read_one(self, frame_number, fps):
        ret, frame = self.video_capture.read()
        if not ret:
            raise StreamEndedError("Could not read frame")
        return Frame(frame_number, frame, frame_number // fps, self.streamer_name)

    def read(self, url, buffer, max: int = -1):
        self.Active = True
        self._acquire(url)
        try:
            self._read(buffer, max)
        except StreamEndedError:
            pass
        self._release()

    def stop(self):
        self.Active = False

    def _read(self, buffer: Queue, max: int = -1):
        video_capture = self.video_capture

        fps = int(video_capture.get(cv.CAP_PROP_FPS))
        if fps > 500:
            fps = 60
        if fps == 0:
            fps = 60

        self.sample_every_count = fps // 8
        for frame in self._yield_frames(fps, max):
            buffer.put(frame)

    def _yield_frames(self, fps, max: int = -1):
        frame_number = 0
        while self.Active:
            item = self._read_one(frame_number, fps)
            if item is None:
                break

            if frame_number % self.sample_every_count == 0:
                yield item
                self.items_read = self.items_read + 1
            frame_number = frame_number + 1
            if 0 < max <= frame_number:
                return

    def _acquire(self, url: str):
        self.video_capture = cv2.VideoCapture(url)

        if not self.video_capture:
            raise NoStreamError("Capture could not open stream")
        if not self.video_capture.isOpened():
            self.video_capture.open(url)

    def _release(self):
        if not self.video_capture:
            return
        self.video_capture.release()


class ClipVideoCapReader(VideoCapReader):
    def __init__(self, streamer_name: str, clip_id: int):
        super(ClipVideoCapReader, self).__init__(streamer_name)
        self.clip_id = clip_id

    def _read_one(self, frame_number, fps):
        ret, frame = self.video_capture.read()
        if not ret:
            raise StreamEndedError("Could not read frame")
        return Frame(frame_number, frame, frame_number // fps, self.streamer_name, self.clip_id)
