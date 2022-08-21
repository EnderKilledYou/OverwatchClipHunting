import threading
from queue import Queue, Empty
from time import sleep

from Monitors.tag_clipper import TagClipper
from tag_clipper.tag_clipper_request import TagClipperRequest
from cloud_logger import cloud_logger
from generic_helpers.something_manager import ThreadedManager
from Database.Twitch.twitch_clip_instance import get_twitch_clip_instance_by_id
from Database.Twitch.tag_clipper_job import update_twitch_clip_job_state
from Database.Twitch.get_tag_and_bag import get_tag_and_bag_by_clip_id


class ScannerMonitor(ThreadedManager):
    tag_clipper: TagClipper

    def __init__(self, tag_clipper: TagClipper):
        super(ScannerMonitor, self).__init__(2, False)
        self.tag_clipper = tag_clipper
        self.return_queue = Queue()
        thread = threading.Thread(target=self.check_return_queue)
        thread.start()
        self._threads.append(thread)
        self._gathered = 0

    def _get_one_ret_queue(self):
        try:


            return self.return_queue.get(False)
        except Empty as e:
            sleep(3)
        finally:
            pass
        return None

    def _do_work(self, job):
        cloud_logger()
        # reset_twitch_clip_job_state()  # reset the jobs that dies half if server crash
        request = self._make_request_from_job(job)
        self.tag_clipper.add_job(request)

    def _make_request_from_job(self, job):
        clip = get_twitch_clip_instance_by_id(job.clip_id)
        request = TagClipperRequest(job.clip_id, get_tag_and_bag_by_clip_id(job.clip_id), clip.broadcaster_name,
                                    clip.video_id, self.return_queue)
        return request

    def check_return_queue(self):

        while self._active:

            returned = self._get_one_ret_queue()
            if returned is None:
                continue
            try:
                if len(returned) == 1:
                    update_twitch_clip_job_state(returned[0], 2)
                else:
                    update_twitch_clip_job_state(returned[0], 3, returned[1])
            except BaseException as b:
                pass
