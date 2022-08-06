import traceback
import cv2
import cv2 as cv
import streamlink

from Ocr.frame import Frame
from Ocr.video_frame_buffer import VideoFrameBuffer


class TwitchVideoFrameBuffer(VideoFrameBuffer):

    def __init__(self, sample_rate: int):
        super(TwitchVideoFrameBuffer, self).__init__()
        self.Active = True
        self.sample_rate = sample_rate

    def _get_frames(self, video_capture, sample_rate):
        fps = int(video_capture.get(cv.CAP_PROP_FPS))
        self.total_frames = (
                                    video_capture.get(cv.CAP_PROP_FRAME_COUNT) // (fps // sample_rate)
                            ) - 1
        frame_number = 0
        self.Capturing = True
        while self.Active and video_capture.isOpened():
            ret, frame = video_capture.read()
            if not ret:
                break
            frame_number += 1
            if frame_number % (fps // sample_rate) != 0:
                continue
            self.buffer.put(Frame(frame_number, frame, frame_number // fps))
        self.Capturing= False

    def buffer_twitch_broadcast(self, broadcaster: str):

        streams = streamlink.streams('https://www.twitch.tv/{0}'.format(broadcaster))
        url = streams['best'].url
        # print(streams)
        cap = cv2.VideoCapture(url)

        if not cap:
            return
        try:

            self._get_frames(cap, self.sample_rate)
        except Exception as e:
            print("Capture thread stopping")
            print(e)

            traceback.print_exc()
        self.Active = False
        try:
            cap.release()
        except Exception as e:
            print("cap release failed")
            print(e)
            print(traceback.format_exc())
