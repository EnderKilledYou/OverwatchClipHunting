import os
import threading
import traceback
from datetime import datetime
from functools import partial
from io import BytesIO
from itertools import chain
from os.path import relpath, abspath
from queue import Queue, Empty
from threading import Lock, Thread
from time import sleep
from pyffmpeg import FFmpeg

from moviepy.video.io.VideoFileClip import VideoFileClip
from streamlink import StreamError
from streamlink.plugins.twitch import TwitchHLSStream
from streamlink.stream.hls import HLSStreamReader

from clip_timestamp import ClipTimeStamp


class StreamClipper:
    _clip_thread: Thread
    clip_requests: Queue
    buffer_lock: Lock
    buffer_fd: BytesIO
    _data_buffer_thread: Thread
    Active: bool = True

    def _trim_buffer_and_clip(self):
        sleep(15)
        while self.Active:
            try:
                print("checking for clips to make")
                self._loop()
            except BaseException as e:
                print(e)
            sleep(15)


    def _loop(self):
        file_name = self._buffer_to_file()
        if file_name is None:
            sleep(2)
            return
        try:
            self._trim_buffer_and_clip_safe(file_name)
        except BaseException as e:
            print(e)
            traceback.print_exc()
        self.safe_delete_file(file_name)

    def _buffer_to_file(self):
        lock_got = False
        file_name = None

        # continue
        try:
            if self.buffer_lock.acquire(True, 2):
                lock_got = True
                file_name = self._write_temp_file_and_trim_buffer()


        except BaseException as e:
            print(e)
        finally:
            if lock_got:  # we can release the lock and now just work on the file copy
                self.buffer_lock.release()

        return file_name

    def safe_delete_file(self, file_name):
        try:
            os.unlink(file_name)
        finally:
            pass

    def _get_clips_requests_safe(self, current_end: int):
        clip_requests = self.get_clip_requests()

        requests = {

        }

        for request in clip_requests:
            if current_end < request.end:
                self.clip_requests.put(request)
            if not request.type in requests:
                requests[request.type] = []
            requests[request.type] = list(
                filter(lambda request2: not (request2.start == request.start and request2.duration <= request.duration),
                       requests[request.type]))
            passed = True
            for request2 in requests[request.type]:
                if request2.start == request.start:
                    passed = False
                    break
            if passed:  # we didn't find any with a longer duration and removed the ones with a shorter or equal
                requests[request.type].append(request)
        return requests

    def get_clip_requests(self):
        clip_requests = []
        while True:
            try:
                clip_requests.append(self.clip_requests.get(False))
            except Empty as e:
                break
        return clip_requests

    def _trim_clip_safe(self, movie: VideoFileClip, clip_time_stamp: ClipTimeStamp):

        start = clip_time_stamp.start - self.dumped_data
        end = clip_time_stamp.end - self.dumped_data
        start = start - clip_time_stamp.start_buffer
        if start < 0:
            start = 0
        end = end + clip_time_stamp.end_buffer
        if end > movie.duration:
            self.clip_request(clip_time_stamp)

            return
        sub_clip: VideoFileClip = movie.subclip(start, end)
        file = self.frame_streamer_name + '_' + str(get_unix_time()) + '.mp4'
        if clip_time_stamp.type == 'elim':
            sub_clip.write_videofile(self.elims_path + file)
        sub_clip.close()

    def _trim_buffer_and_clip_safe(self, file_name):
        if self.clip_requests.qsize() < 1:
            sleep(1)
            return
        movie: VideoFileClip = VideoFileClip(file_name)
        try:
            self._process_requests(movie)
        finally:
            movie.close()

    def _process_requests(self, movie):
        requests = self._get_clips_requests_safe(movie.duration + self.dumped_data)
        for key in requests:
            request: ClipTimeStamp
            for request in requests[key]:
                self._trim_clip_safe(movie, request)

    def _write_temp_file_and_trim_buffer(self):
        unix_time = str(get_unix_time())
        file_name = abspath(self.frame_streamer_name + unix_time + '.mp4')
        file_name_ts = abspath(self.frame_streamer_name + unix_time + '.ts')

        with open(file_name_ts, "wb") as output:
            output.write(self.buffer_fd.getbuffer())

        file_name = opencv_video_save_as(file_name_ts, file_name)
        os.unlink(file_name_ts)
        if not os.path.exists(file_name):
            print("couldn't convert data")
            return None
        print("opening " + file_name)

        movie: VideoFileClip = VideoFileClip(file_name)

        try:
            movie_duration = movie.duration
            if movie_duration > 150:
                self.truncate_data(movie_duration)
        finally:
            movie.close()

        return file_name

    def truncate_data(self, movie_duration):
        pos = self.buffer_fd.tell()
        excess = movie_duration / 150
        excess_fraction = (1 / excess)
        clip = pos - pos * excess_fraction
        time = movie_duration - movie_duration * excess_fraction
        self.dumped_data += time
        self.buffer_fd.seek(clip)
        self.buffer_fd.truncate(clip)

    def _data_buffer(self, stream: TwitchHLSStream, chunk_size=8192):
        try:
            reader: HLSStreamReader = stream.open()
            prebuffer = reader.read(chunk_size)

            stream_iterator = chain(
                [prebuffer],
                iter(partial(reader.read, chunk_size), b"")
            )
        except StreamError as st:
            print("Error opening data stream")
            self.Active = False
            return

        try:
            for data in stream_iterator:
                if not self.Active:
                    break
                if not self.buffer_lock.acquire(True, 1):
                    continue
                self.buffer_fd.write(data)
                self.buffer_lock.release()


        except BaseException as e:
            print("Error buffering to file:")
            print(e)

        finally:
            safe_close(self.buffer_fd)
            safe_close(reader)

    def clip_request(self, clip_time_stamp: ClipTimeStamp):
        self.clip_requests.put(clip_time_stamp)

    def start_buffer(self, streamer_config, streams):
        data_stream = streams['best']
        if streamer_config.buffer_prefers_quality in streams:
            data_stream = streams[streamer_config.buffer_prefers_quality]
        self._data_buffer_thread = threading.Thread(target=self._data_buffer, args=[data_stream])
        self._data_buffer_thread.start()
        self._clip_thread = threading.Thread(target=self._trim_buffer_and_clip, args=[])
        self._clip_thread.start()

    def __init__(self, frame_streamer_name):
        self._clip_thread = None
        self.frame_streamer_name = frame_streamer_name
        self.elims_path = abspath('./clips/' + frame_streamer_name + '/elims/')
        if not os.path.exists(self.elims_path):
            os.makedirs(self.elims_path)
        self.buffer_fd = BytesIO()
        self.buffer_lock = threading.Lock()
        self.clip_requests = Queue()
        self._data_buffer_thread = None
        self.dumped_data = 0


def get_unix_time():
    presentDate = datetime.now()
    unix_timestamp = datetime.timestamp(presentDate) * 1000
    return unix_timestamp


def safe_close(item):
    try:
        item.close()
    finally:
        pass

import vlc
def opencv_video_save_as(video_path, save_path):
    """
    video save as video
    :param video_path:
    :param save_path:
    :return:
    """
    ff = FFmpeg()
    output_file = ff.convert(video_path, save_path)
    print(output_file)
    return output_file
