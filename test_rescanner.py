import traceback

from Ocr.re_scaner import ReScanner
from Database.tag_and_bag import add_tag_and_bag_request
from Database.Twitch.twitch_clip_instance import add_twitch_clip_instance_from_api, \
    delete_twitch_clip_instance, get_twitch_clip_instance_by_video_id
from twitch_helpers import get_twitch_api


def test_rescanner():
    twitch_api = get_twitch_api()
    try:
        bag_and_tag_clip(twitch_api)
    except BaseException as b:
        print(b)
        traceback.print_exc()
        pass


def bag_and_tag_clip(twitch_api):
    video_id = 'IncredulousRelatedCheeseBudStar-mwq2wt5iKH6CLmNO'
    by_video_id = get_twitch_clip_instance_by_video_id(video_id)
    if by_video_id:
        delete_twitch_clip_instance(by_video_id)
    clip_resp = twitch_api.get_clips(clip_id=video_id)
    clip = add_twitch_clip_instance_from_api(clip_resp['data'][0], 'elim')
    tag_bag = add_tag_and_bag_request(clip.id)
    print(clip.thumbnail_url)

    scanner = ReScanner()
    scanner.start()
    scanner.add_job(clip.id)
    scanner.join(500)
