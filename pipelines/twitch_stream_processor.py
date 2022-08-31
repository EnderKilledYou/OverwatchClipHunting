import cv2

from pipelines.pipe_line_image_queue import get_pipe_line_image_queue
from pipelines.queue_boss import QueueBossBase


class TwitchStreamProcessor(QueueBossBase):
    def _process(self, job_tuple):
        url, broadcaster = job_tuple
        pipe_line_queue = get_pipe_line_image_queue()
        video_capture = cv2.VideoCapture(url)
        frame_number = 0
        while video_capture.isOpened():
            ret, frame = video_capture.read()
            pipe_line_queue.add_work((frame, frame_number))
            frame_number = frame_number + 1
