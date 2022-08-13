import traceback

import cv2
import cv2 as cv
import streamlink

from Clipper.clipper import Clipper
from Ocr.frame import Frame

from Clipper.get_unix_time import get_unix_time
from Ocr.video_frame_buffer import VideoFrameBuffer
from config.streamer_configs import get_streamer_config


class TwitchVideoFrameBuffer(VideoFrameBuffer):
    frame_streamer_name: str = ''
    file_name = ''

    def __init__(self, broadcaster: str, sample_rate: int):
        super(TwitchVideoFrameBuffer, self).__init__()

        self.fps = 60
        self.broadcaster = broadcaster
        self.stream_clipper = Clipper(self.frame_streamer_name)
        self.Active = True
        self.sample_rate = sample_rate

    def watch_streamer(self):
        self.buffer_twitch_broadcast()
        self.Active = False
        print("Exiting watch of " + self.broadcaster)
        # if not get_streamer_config(self.broadcaster).wait_for_mode:
        #     return self.buffer_twitch_broadcast()
        # while self.Active:
        #     print("checking for " + self.broadcaster)
        #     self.buffer_twitch_broadcast()

    def buffer_twitch_broadcast(self):

        streams = streamlink.streams('https://www.twitch.tv/{0}'.format(self.broadcaster))
        if 'best' not in streams:
            print("stream offline")
            self.Active = False
            return
        self.file_name = "{0}_{1}.ts".format(self.broadcaster, str(get_unix_time()))
        ocr_stream = streams['best']
        streamer_config = get_streamer_config(self.broadcaster)
        data_stream = streams['best']
        if streamer_config.buffer_prefers_quality in streams:
            data_stream = streams[streamer_config.buffer_prefers_quality]

        if '720p60' in streams:
            ocr_stream = streams['720p60']
            self.fps = 60
        else:
            for stream_res in streams:
                if not stream_res.endswith('p60'):
                    continue
                ocr_stream = streams[stream_res]
                self.fps = 60

        if streamer_config.buffer_data:
            self.stream_clipper.start(data_stream)

        self._capture_stream(ocr_stream)

    def _capture_stream(self, stream):
        url = stream.url
        self.capture_url_or_file(url)

    def capture_url_or_file(self, url):
        video_capture = cv2.VideoCapture(url)
        if not video_capture:
            print("Capture could not open stream")
        #     return
        try:

            fps = int(video_capture.get(cv.CAP_PROP_FPS))
            if fps > 500:
                fps = 60
            frame_number = 0
            self.Capturing = True
            while self.Active and video_capture.isOpened():
                ret, frame = video_capture.read()
                if not ret:
                    break
                frame_number += 1
                if frame_number % (fps // self.sample_rate) != 0:
                    continue
                self.buffer.put(
                    Frame(frame_number, frame, frame_number // fps, self.frame_streamer_name, self.file_name))
            self.Capturing = False
        except Exception as e:

            print(e)

            traceback.print_exc()
        try:
            video_capture.release()
        except Exception as e:
            print("cap release failed")
            print(e)
            print(traceback.format_exc())

        print("Capture thread stopping")
