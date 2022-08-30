import threading
from queue import Queue
from time import sleep

import cv2
import cv2 as cv
import numpy

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
        self.sample_every_count = 5
        self.items_read = 0
        self.items_drained = 0
        self.fps = 1
        self.video_capture = None
        self.error_count = 0
        self.clip_id = -1

    def __del__(self):
        print(f"VideoCapReader Del")
        self._count_lock = None
        if hasattr(self, 'video_capture') and self.video_capture is not None:
            print("releasing video capture")
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

    def _read_one2(self, frame_number, fps, video_capture):

        #   if frame_number > 0 and frame_number % self.fps == 0:
        # print(f"Sleeping off empty buffer {self.streamer_name}")
        #        sleep_amount = .3
        #        sleep(sleep_amount)

        ret, frame = video_capture.read()

        if ret:
            if frame is not None:
                if frame_number % self.sample_every_count != 0:
                    del frame
                    frame = None
                    return None
                if numpy.sum(frame) == 0:
                    print("Got empty frame")
                    del frame
                    frame = None
                    return None
                return Frame(frame_number, frame, frame_number // fps, self.streamer_name, self.clip_id)
            return None #rare bug in vcap

        print(f"could not get frame {self.streamer_name}")

        raise StreamEndedError("Could not read frame")

    def _read_one(self, frame_number, fps):

        self.video_capture.grab()

        if frame_number % self.sample_every_count != 0:
            return None

        ret, frame = self.video_capture.retrieve()

        if ret:
            return Frame(frame_number, frame, frame_number // fps, self.streamer_name, self.clip_id)

        print(f"Stream could not be read from {self.streamer_name}")
        raise StreamEndedError("Could not read frame")

    def read(self, url, buffer):
        self.Active = True
        video_capture = self._acquire2(url)
        try:
            self._read(buffer)
        except StreamEndedError:
            pass

    def get_stats(self):

        qsize = self.count()
        frames_pending = qsize * self.sample_every_count
        frames_finished = self.items_drained * self.sample_every_count
        back_fill_seconds = frames_pending // self.fps

        return qsize, frames_finished, frames_finished, back_fill_seconds, self.fps, self.sample_every_count, self.items_read

    def read2(self, url, buffer, cancel_token, stats_callback=None):
        self.Active = True
        print(f"Opening {url} for {self.streamer_name}")
        video_capture = self._acquire2(url)
        if video_capture is None:
            print("no video capture")
            return
        try:
            self._read2(buffer, video_capture, cancel_token, stats_callback)
        except StreamEndedError:
            pass
        try:
            video_capture.release()
        except BaseException as b:
            cloud_logger.cloud_error_logger(b)
        finally:
            del video_capture

    def readYield(self, url, cancel_token):

        self._acquire(url)
        try:

            fps = int(self.video_capture.get(cv.CAP_PROP_FPS))
            if fps > 500:
                fps = 60
            if fps < 10:
                fps = 60
            self.fps = fps
            self.sample_every_count = fps // sample_frame_rate
            return self._yield_frames(fps, cancel_token)
        except StreamEndedError:
            try:
                self._release()
            except:
                pass
            pass

    def stop(self):
        self.Active = False

    def _read2(self, buffer: Queue, video_capture, cancel_token, stats_callback=None):

        fps = int(video_capture.get(cv.CAP_PROP_FPS))
        if fps > 500:
            fps = 60
        if fps < 10:
            fps = 60
        self.fps = fps
        frame_number = 0

        self.sample_every_count = fps // sample_frame_rate
        cloud_logger.cloud_message(
            f"Starting sampling.. sampling {fps} /  {sample_frame_rate} = {self.sample_every_count}")

        while not cancel_token.cancelled and self._next_frame2(frame_number, buffer, video_capture):
            frame_number = frame_number + 1
            if stats_callback is not None and frame_number % 100 == 0:
                stats_callback(self.get_stats())

    def _next_frame2(self, frame_number, buffer: Queue, video_capture):
        item = self._read_one2(frame_number, self.fps, video_capture)
        if item is None:
            return True

        buffer.put(item)
        self.incr_items_read()

        return True

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
        try:
            while self.Active and self._next_frame(frame_number, buffer):
                frame_number = frame_number + 1
        finally:
            try:
                self.video_capture.release()
            except BaseException as b:
                cloud_logger.cloud_error_logger(b)
                pass
        print("cleared")

    def _next_frame(self, frame_number, buffer: Queue):
        if self.count() > 100:
            # print(f"transfer full, waiting {self.streamer_name}")
            sleep(3)

        item = self._read_one(frame_number, self.fps)
        if item is None:
            return True

        if frame_number > 0 and frame_number % 10 == 0 and self.count() == 0:
            # print(f"Sleeping off empty buffer {self.streamer_name}")
            sleep(1)  # let the video cap have some time to buffer
        buffer.put(item)

        self.incr_items_read()
        return True

    def _yield_frames(self, fps, cancel_token):
        frame_number = 0
        while not cancel_token.cancelled:
            try:
                item = self._read_one(frame_number, fps)
            except StreamEndedError:
                break
            frame_number = frame_number + 1
            if item is None:
                continue

            yield item
            self.incr_items_read()

    def _acquire2(self, url: str):
        video_capture = cv2.VideoCapture(url)

        video_capture.set(cv2.CAP_PROP_BUFFERSIZE, 15)
        if not video_capture:
            raise None
        video_capture.open(url)
        return video_capture

    def _acquire(self, url: str):
        self.video_capture = cv2.VideoCapture(url, apiPreference=cv.CAP_OPENCV_MJPEG)
        self.video_capture.set(cv2.CAP_PROP_BUFFERSIZE, 1)
        if not self.video_capture:
            raise NoStreamError("Capture could not open stream")
        if not self.video_capture.isOpened():
            self.video_capture.open(url)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.stop()

    def _release(self):

        pass


class ClipVideoCapReader(VideoCapReader):
    def __init__(self, streamer_name: str, clip_id: int):
        super(ClipVideoCapReader, self).__init__(streamer_name)
        self.clip_id = clip_id
        self.sample_every_count = 30
