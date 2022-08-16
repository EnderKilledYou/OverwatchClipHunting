from Ocr.re_scaner import ReScanner, RescannerRequest
from Ocr.tag_clipper import TagClipper
from something_manager import ThreadedManager
from Database.Twitch.twitch_clip_instance import get_twitch_clip_instance_by_id
from Database.Twitch.twitch_clip_tag import get_tag_and_bag_by_id, get_tag_and_bag_by_clip_id


def make_rescanner_job_from_clip_id(clip_id):
    clip = get_twitch_clip_instance_by_id(clip_id)
    if clip is None:
        return None

    url = clip.thumbnail_url.split("-preview", 1)[0] + ".mp4"
    return RescannerRequest(tag_and_bag.id, url, clip.broadcaster_name, clip_id)


class ReScannerMonitor(ThreadedManager):
    tag_clipper: TagClipper

    def __init__(self, rescanner: ReScanner):
        super(ReScannerMonitor, self).__init__(2, False)
        self.rescanner = rescanner



    def _do_work(self, clip_id):
        # reset_twitch_clip_job_state()  # reset the jobs that dies half if server crash
        request = make_rescanner_job_from_clip_id(clip_id)
        self.rescanner.add_job(request.id)
