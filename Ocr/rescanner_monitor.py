import threading
from queue import Queue, Empty
from time import sleep

from Ocr.re_scaner import ReScanner, RescannerRequest
from Ocr.tag_clipper import TagClipper
from Ocr.tag_clipper_request import TagClipperRequest
from something_manager import ThreadedManager
from twitch.twitch_clip_instance import get_twitch_clip_instance_by_id, update_twitch_clip_job_state
from twitch.twitch_clip_tag import get_tag_and_bag_by_clip_id, get_tag_and_bag_by_id


class ReScannerMonitor(ThreadedManager):
    tag_clipper: TagClipper

    def __init__(self, rescanner: ReScanner):
        super(ReScannerMonitor, self).__init__(2, False)
        self.rescanner = rescanner

    def add_job(self, clip_id: int):
        self.buffer.put(clip_id)

    def _do_work(self, clip_id):
        # reset_twitch_clip_job_state()  # reset the jobs that dies half if server crash
        request = self._make_request_from_job(clip_id)
        self.rescanner.add_job(request)

    def _make_request_from_job(self, clip_id):
        clip = get_twitch_clip_instance_by_id(clip_id)
        if clip is None:
            return None
        tag_and_bag = get_tag_and_bag_by_id(clip_id)
        if tag_and_bag is None:
            return None
        url = clip.thumbnail_url.split("-preview", 1)[0] + ".mp4"
        return RescannerRequest(tag_and_bag.id, url, clip.broadcaster_name, clip_id)
