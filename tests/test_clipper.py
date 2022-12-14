from Monitors.tag_clipper import TagClipper
from tag_clipper.tag_clipper_request import TagClipperRequest
from Database.Twitch.twitch_clip_instance import get_twitch_clip_instance_by_video_id
from Database.Twitch.get_tag_and_bag import get_tag_and_bag_by_clip_id


def test_tag_clipper():
    return
    tag_clipper = TagClipper()
    # api = get_twitch_api()
    # bag_and_tag_clip(api)
    video_id = 'IncredulousRelatedCheeseBudStar-mwq2wt5iKH6CLmNO'
    clip = get_twitch_clip_instance_by_video_id(video_id)
    clip_queue = get_tag_and_bag_by_clip_id(clip.id)

    for a in clip_queue:
        if a.tag_duration < 4:
            a.clip_end += 4
            if a.clip_start > 4:
                a.clip_start -= 4
    tag_clipper.add_job(TagClipperRequest(clip.id,  clip_queue, clip.broadcaster_name,video_id))
    tag_clipper.start()
    tag_clipper.join(500)

