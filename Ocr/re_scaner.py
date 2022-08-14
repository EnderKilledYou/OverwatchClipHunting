import os
from os.path import abspath

from queue import Empty

import moviepy.config as mpy_conf

mpy_conf.change_settings({'FFMPEG_BINARY': "C:\\ProgramData\\chocolatey\\bin\\ffmpeg.exe",
                          })

from Ocr.VideoCapReader import VideoCapReader, StreamEndedError, ClipVideoCapReader
from Ocr.overwatch_clip_reader import OverwatchClipReader
from something_manager import ThreadedManager
from twitch.tag_and_bag import update_tag_and_bag_scan_progress, \
    if_tag_cancel_request_exists, update_tag_and_bag_scan_scan_error


class InvalidFpsError(BaseException):
    pass


tmp_path = abspath(
    './tmp')
if not os.path.exists(tmp_path):
    os.makedirs(tmp_path)


class RescannerRequest:
    def __init__(self, tag_id: int, mp4_url: str, broadcaster, clip_id: int ):
        self.tag_id = tag_id
        self.broadcaster = broadcaster
        self.mp4_url = mp4_url
        self.clip_id = clip_id


        # self.reader = ClipVideoCapReader(self._broadcaster, clip_id)


class ReScanner(ThreadedManager):
    _frame_count: int
    _reader: VideoCapReader

    # self._instance.thumbnail_url.split("-preview", 1)[0] + ".mp4"
    def __init__(self):
        super(ReScanner, self).__init__(1)
        self._frame_count = 0
        self.matcher = OverwatchClipReader()

    def _do_work(self, job: RescannerRequest):
        try:
            reader = ClipVideoCapReader(job.broadcaster, job.clip_id)
            reader.read(job.mp4_url, self.buffer)

        except StreamEndedError:
            pass
        except BaseException as e:
            print(e)
            update_tag_and_bag_scan_scan_error(job.tag_id, str(e))
            return

        try:
            self._scan_clip(job)
        except BaseException as e:
            print(e)
            update_tag_and_bag_scan_scan_error(job.tag_id, str(e))
            return

    def _stop(self):
        self._reader.stop()

    def _scan_clip(self, job: RescannerRequest):
        size = self.buffer.qsize()
        frame_number = 0
        try:
            while True:
                frame = self.buffer.get(False)
                self.matcher.ocr(frame)
                self._frame_count += 1
                percent_done = frame_number + 1 / size
                if int(percent_done) % 15 == 0:
                    if if_tag_cancel_request_exists(job.tag_id):
                        return
                    update_tag_and_bag_scan_progress(job.tag_id, percent_done)
        except Empty:
            pass
        except BaseException as b:
            pass

        update_tag_and_bag_scan_progress(job.tag_id, 1)
