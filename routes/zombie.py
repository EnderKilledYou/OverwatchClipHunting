from os import abort

from flask import Blueprint, request

from Database.Twitch.twitch_clip_instance import get_twitch_clip_instance_by_video_id, add_twitch_clip_instance_from_api
from Database.Twitch.twitch_clip_tag import add_twitch_clip_tag_request
from twitch_helpers import get_twitch_api

zombie_route = Blueprint('zombie', __name__)


class ZombieKey:
    pass

    def match_key(self) -> bool:
        return True


api_keys = [ZombieKey('abc')]


@zombie_route.route('/<api_key>/zombie_tag')
def zombie_tag(api_key: str):
    if api_key is None or len(api_key < 10):
        print("missing params2")
        abort(400)
    if not request.json or 'clip' not in request.json or 'tag' not in request.json:
        print("missing params")
        abort(400)
    if not check_key(api_key):
        abort(401)

    twitch_api = get_twitch_api()
    clip = request.json['clip']
    tag = request.json['tag']
    clip = get_twitch_clip_instance_by_video_id(clip['video_id'])
    clip_resp = twitch_api.get_clips(clip_id=clip['video_id'])
    if not clip_resp or 'data' not in clip_resp or len(clip_resp['data']) == 0:
        return {"success": False, "error": "clip doesn't on twitch"}
    clip = get_twitch_clip_instance_by_video_id(clip['video_id'])
    if not clip:
        clip = add_twitch_clip_instance_from_api(clip_resp['data'][0], 'elim')
    add_twitch_clip_tag_request(clip_id=clip['video_id'], tag=tag['tag'], tag_amount=tag['tag_amount'],
                                tag_duration=tag['tag_duration'], tag_start=tag['tag_start'], )


def check_key(api_key):
    passed = False
    for key in api_keys:
        if key.match_key(api_key):
            passed = True

