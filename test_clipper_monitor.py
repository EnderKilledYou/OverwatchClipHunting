from Database.Twitch.twitch_clip_instance_scan_job import add_twitch_clip_scan
from Ocr.tag_clipper_monitor import TagMonitor
from Ocr.tag_clipper import TagClipper

from Database.Twitch.twitch_clip_instance import get_twitch_clip_instance_by_video_id
from Database.Twitch.tag_clipper_job import get_twitch_clip_job, reset_twitch_clip_job_state, add_twitch_clip_job
from Database.Twitch.twitch_clip_tag import get_tag_and_bag_by_clip_id


def test_tag_clipper_monitor():
    return
    reset_twitch_clip_job_state()
    tag_clipper = TagClipper()
    tag_monitor = TagMonitor(tag_clipper)
    # api = get_twitch_api()
    # bag_and_tag_clip(api)
    video_id = 'IncredulousRelatedCheeseBudStar-mwq2wt5iKH6CLmNO'

    clip = get_twitch_clip_instance_by_video_id(video_id)
    job = get_twitch_clip_job()
    if job is None:
        clip_queue = get_tag_and_bag_by_clip_id(clip.id)
        for a in clip_queue:
            clip_scan = add_twitch_clip_job(a.clip_id, a.id)

        add_twitch_clip_scan(clip.id)
        job = get_twitch_clip_job()

    assert job is not None
    tag_monitor.add_job(job)
    tag_clipper.start()
    tag_monitor.start()
    tag_monitor.join(500)
    tag_clipper.join(500)
