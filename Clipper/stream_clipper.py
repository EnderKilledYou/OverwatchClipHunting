# import os
# import threading
# import traceback
# from io import BytesIO
# from os.path import abspath
# from threading import Lock, Thread
# from time import sleep
#
# from moviepy.video.io.VideoFileClip import VideoFileClip
#
# from Clipper.clip_timestamp import ClipTimeStamp
# from Clipper.clipper import Clipper
# from Clipper.convert_video import opencv_video_save_as
# from Clipper.get_unix_time import get_unix_time
#
#
#
# class StreamClipper:
#     _clip_thread: Thread
#
#     buffer_lock: Lock
#
#     _data_buffer_thread: Thread
#     Active: bool = True
#
#     def _loop(self):
#         file_name = self._buffer_to_file()
#         if file_name is None:
#             sleep(2)
#             return
#         try:
#             self._trim_buffer_and_clip_safe(file_name)
#         except BaseException as e:
#             print(e)
#             traceback.print_exc()
#         self.safe_delete_file(file_name)
#
#     def _buffer_to_file(self):
#         lock_got = False
#         file_name = None
#
#         # continue
#         try:
#             if self.buffer_lock.acquire(True, 2):
#                 lock_got = True
#                 file_name = self._write_temp_file_and_trim_buffer()
#
#
#         except BaseException as e:
#             print(e)
#         finally:
#             if lock_got:  # we can release the lock and now just work on the file copy
#                 self.buffer_lock.release()
#
#         return file_name
#
#     def _process_requests(self, movie):
#         requests = self._get_clips_requests_safe(movie.duration + self.dumped_data)
#         for key in requests:
#             for request in requests[key]:
#                 self._trim_clip_safe(movie, request)
#
#     def _write_temp_file_and_trim_buffer(self):
#         unix_time = str(get_unix_time())
#         file_name = abspath(self.frame_streamer_name + unix_time + '.mp4')
#         file_name_ts = abspath(self.frame_streamer_name + unix_time + '.ts')
#
#         with open(file_name_ts, "wb") as output:
#             output.write(self.buffer_fd.getbuffer())
#
#         opencv_video_save_as(file_name_ts, file_name)
#         os.unlink(file_name_ts)
#         if not os.path.exists(file_name):
#             print("couldn't convert data")
#             return None
#         print("opening " + file_name)
#
#         with VideoFileClip(file_name) as movie:
#             movie_duration = movie.duration
#             if movie_duration > 150:
#                 self.truncate_data(movie_duration)
#
#         return file_name
#
#     def clip_request(self, clip_time_stamp: ClipTimeStamp):
#         self.clipper.put(clip_time_stamp)
#
#     def start_buffer(self, ):
#         self.clipper.start(self.stream)
#
#     def __init__(self, frame_streamer_name, stream):
#         self._clip_thread = None
#         self.stream = stream
#         self.frame_streamer_name = frame_streamer_name
#         self.elims_path = abspath('./clips/' + frame_streamer_name + '/elims/')
#         if not os.path.exists(self.elims_path):
#             os.makedirs(self.elims_path)
#         self.buffer_fd = BytesIO()
#         self.buffer_lock = threading.Lock()
#         self.clipper = Clipper(frame_streamer_name)
#
#         self._data_buffer_thread = None
#         self.dumped_data_seconds = 0
#
#
