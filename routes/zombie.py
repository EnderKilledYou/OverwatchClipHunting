from flask import Blueprint, request

from Database.api_user import add_zombie, get_zombies

zombie_route = Blueprint('zombie', __name__)
from os import abort
from time import sleep
from Database.Twitch.twitch_clip_instance import get_twitch_clip_instance_by_video_id, add_twitch_clip_instance_from_api
from Database.Twitch.twitch_clip_tag import add_twitch_clip_tag_request
from sharp_api import get_sharp
from something_manager import ThreadedManager
from twitch_helpers import get_twitch_api

sharp = get_sharp()


class ZombieKey:
    pass

    def __init__(self, match_val):
        self.match_val = match_val

    def match_key(self) -> bool:
        return True


api_keys = [ZombieKey('nC8*l$x4+oobm=EU5WJvZYu=PJXE9OBhP7=')]


@sharp.function()
def zombie_add(name: str):
    try:
        zombie = add_zombie(name)
        return {'success': True, 'zombie': zombie.to_dict()}
    except BaseException as e:
        return {'success': False, 'error': str(e)}


@sharp.function()
def zombie_list(name: str):
    try:
        zombies = get_zombies()
        zombie_data = list(map(lambda x: x.to_dict(), zombies))
        return {'success': True, 'zombie': zombie_data.to_dict()}
    except BaseException as e:
        return {'success': False, 'error': str(e)}


@sharp.function()
def zombie_task_list():
    try:
        zombies = get_zombies()
        zombie_data = list(map(lambda x: x.to_dict(), zombies))
        return {'success': True, 'zombie': zombie_data.to_dict()}
    except BaseException as e:
        return {'success': False, 'error': str(e)}


# @zombie_route.route('/add_zombie')
@sharp.function()
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


class BrainScanner(ThreadedManager):

    def _start(self):
        while self._active:
            sleep(6)

    def _do_work(self, item):
        pass

    def __init__(self):
        super(BrainScanner, self).__init__(1, False)


def check_key(api_key):
    passed = False
    for key in api_keys:
        if key.match_key(api_key):
            passed = True
    return passed
