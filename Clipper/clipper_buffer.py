import os
import threading
import traceback
from functools import partial
from io import BytesIO
from itertools import chain
from os.path import abspath
from threading import Lock

from moviepy.video.io.VideoFileClip import VideoFileClip
from streamlink import StreamError
from streamlink.plugins.twitch import TwitchHLSStream
from streamlink.stream.hls import HLSStreamReader

from Clipper.clip_file import ClipFile
from Clipper.convert_video import opencv_video_save_as
from Clipper.safe_close import safe_close
from Clipper.get_unix_time import get_unix_time


class ClipBuffer:
    Active: bool
    buffer_lock: Lock
    stream: TwitchHLSStream
    buffer_fd: BytesIO

    def __init__(self):
        self.Active = True
        self.dumped_data_seconds = 0
        self.end = 0
        self.buffer_lock = threading.Lock()

    def _truncate_buffer(self, movie_duration):
        pos = self.buffer_fd.tell()
        excess = movie_duration / 150
        excess_fraction = (1 / excess)
        clip = pos - pos * excess_fraction
        time = movie_duration - movie_duration * excess_fraction
        self.dumped_data_seconds += time
        self.buffer_fd.seek(clip)
        self.buffer_fd.truncate(clip)

    def buffer_to_file(self) -> ClipFile:
        try:
            lock_acquired = self.buffer_lock.acquire(True, 2)
            if lock_acquired:
                file_path = self._write_temp_file_and_trim_buffer()
                duration = self._trim_clip_buffer(file_path)
                return ClipFile(file_path=file_path, time_start=self.dumped_data_seconds,
                                time_end=self.dumped_data_seconds + duration)
        except BaseException as e:
            print(e)
            traceback.print_exc()
        finally:
            if lock_acquired:
                self.buffer_lock.release()

        return None

    def _write_temp_file_and_trim_buffer(self):
        unix_time = str(get_unix_time())
        file_path = abspath(self.frame_streamer_name + unix_time + '.mp4')
        file_name_ts = abspath(self.frame_streamer_name + unix_time + '.ts')

        with open(file_name_ts, "wb") as output:
            output.write(self.buffer_fd.getbuffer())
        print("converting " + file_path)
        opencv_video_save_as(file_name_ts, file_path)
        print("converted " + file_path)
        os.unlink(file_name_ts)

        if not os.path.exists(file_path):
            print("couldn't convert data")
            return None

        return file_path

    def _trim_clip_buffer(self, file_name):
        with VideoFileClip(file_name) as movie:
            movie_duration = movie.duration
            if movie_duration <= 150:
                return
            self._truncate_buffer(movie_duration)

        return movie_duration

    def stream_reader(self, stream: TwitchHLSStream, chunk_size=8192):
        reader: HLSStreamReader = stream.open()
        stream_iterator = self._create_stream_iterator(chunk_size, reader)
        if stream_iterator is None:
            return

        try:
            self._read_stream_iterator(stream_iterator)

        except BaseException as e:
            print("Error buffering to file:")
            print(e)
            traceback.print_exc()
        finally:
            safe_close(self.buffer_fd)
            safe_close(reader)

    def _read_stream_iterator(self, stream_iterator):
        tmp = BytesIO()
        for data in stream_iterator:
            if not self.Active:
                return
            self._write_to_buffer_with_lock(data, tmp)

    def _create_stream_iterator(self, chunk_size, reader):
        try:
            prebuffer = reader.read(chunk_size)

            stream_iterator = chain(
                [prebuffer],
                iter(partial(reader.read, chunk_size), b"")
            )
        except StreamError as st:
            print("Error opening data stream")
            self.Active = False
            return None
        return stream_iterator

    def _write_to_buffer_with_lock(self, data, tmp: BytesIO):
        if not self.buffer_lock.acquire(True, 5):
            tmp.write(data)  # can't get lock so store in local buffer
            return
        try:
            if tmp.tell() > 0:
                tmp.seek(0)  # seek to start
                self.buffer_fd.write(tmp.read(-1))
                tmp.seek(0)
                tmp.truncate(0)
            self.buffer_fd.write(data)
            self.buffer_lock.release()
        except BaseException as b:
            print(b)
            traceback.print_exc()
        finally:
            self.buffer_lock.release()
