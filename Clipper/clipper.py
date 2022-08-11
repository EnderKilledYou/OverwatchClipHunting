import os
import threading
from queue import Queue, Empty

from moviepy.video.io.VideoFileClip import VideoFileClip
from streamlink.plugins.twitch import TwitchHLSStream

from Clipper.clip_timestamp import ClipTimeStamp
from Clipper.clipper_buffer import ClipBuffer
from Clipper.clip_file import ClipFile
from Clipper.get_unix_time import get_unix_time


class Clipper:

    clip_requests: Queue
    clip_files: []

    def __init__(self, frame_streamer_name):
        self._clip_thread = None
        self._data_buffer_thread = None
        self.buffer = ClipBuffer()
        self.frame_streamer_name = frame_streamer_name
        self.Active = True

    def _get_clips_requests_safe(self, current_end: int):
        clip_requests = self.get_clip_requests()

        requests = {

        }
        clip_list = []
        for request in clip_requests:
            if current_end < request.end:
                self.clip_requests.put(request)
            else:
                clip_list.append(request)

        return clip_list

    def _process_requests(self, movie):
        requests = self._get_clips_requests_safe(movie.duration + self.dumped_data)
        for request in requests:
            self._trim_clip_safe(movie, request)

    def _trim_clip_safe(self, movie: VideoFileClip, clip_time_stamp: ClipTimeStamp):

        start = clip_time_stamp.start - self.buffer.dumped_data_seconds
        end = clip_time_stamp.end - self.dumped_data_seconds
        start = start - clip_time_stamp.start_buffer
        if start < 0:
            start = 0
        end = end + clip_time_stamp.end_buffer
        if end > movie.duration:
            self.clip_requests.put(clip_time_stamp)

            return
        sub_clip: VideoFileClip = movie.subclip(start, end)
        file = self.frame_streamer_name + '_' + str(get_unix_time()) + '.mp4'
        if clip_time_stamp.type == 'elim':
            sub_clip.write_videofile(self.elims_path + file)
        sub_clip.close()

    def _trim_buffer_and_clip_safe(self, file_name):
        if self.clip_requests.qsize() < 1:
            return
        if file_name is None:
            return
        with VideoFileClip(file_name) as movie:
            self._process_requests(movie)

    def get_clip_requests(self):
        clip_requests = []
        while True:
            try:
                clip_requests.append(self.clip_requests.get(False))
            except Empty as e:
                break
        return clip_requests

    def put(self, clip_time_stamp: ClipTimeStamp):
        self.clip_requests.put(clip_time_stamp)

    def clip_file(self, clip_file: ClipFile):
        self.clip_files.append(clip_file)

    def _safe_delete_file(self, file_name):
        try:
            if os.path.exists(file_name):
                os.unlink(file_name)
        finally:
            pass

    def _trim_buffer_and_clip(self):
        while self.Active:
            try:

                clip_requests_size = self.clip_requests.qsize()
                if clip_requests_size < 1:
                    print("There are no clips to make")
                    continue
                print("There are {0} clips to make".format(str(clip_requests_size)))

                file = self.buffer.buffer_to_file()
                if file is not None:
                    self._trim_buffer_and_clip_safe(file)
            except BaseException as e:
                print(e)

    def start(self, stream: TwitchHLSStream):
        self._data_buffer_thread = threading.Thread(target=self.buffer.stream_reader, args=[stream])
        self._data_buffer_thread.start()
        self._clip_thread = threading.Thread(target=self._trim_buffer_and_clip, args=[])
        self._clip_thread.start()


