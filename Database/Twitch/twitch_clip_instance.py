from typing import Tuple

from dateutil.parser import isoparse
from sqlalchemy_serializer import SerializerMixin

from Database.Twitch.dict_to_class import Dict2Class
from OrmHelpers.BasicWithId import BasicWithId
from config.db_config import db


class TwitchClipInstance(db.Model, SerializerMixin):
    serialize_rules = ()
    serialize_only = (
        'id', 'video_id', 'video_url', 'created_at', 'thumbnail_url',
        'title', 'broadcaster_name', 'type', 'vod_offset', 'duration')
    id = db.Column(db.Integer, primary_key=True)
    video_id = db.Column(db.String(90), unique=True)
    video_url = db.Column(db.String(900), unique=True)
    created_at = db.Column(db.DateTime)
    thumbnail_url = db.Column(db.String(900))
    title = db.Column(db.Unicode(900))
    broadcaster_name = db.Column(db.String(90))
    type = db.Column(db.String(90))
    vod_offset = db.Column(db.Integer)
    duration = db.Column(db.Integer)
    file_path = db.Column(db.String(900))

    def __init__(self, from_api={}):
        if 'id' in from_api:
            from_api['video_id'] = from_api['id']
            from_api.pop('id')
        for key in from_api:
            setattr(self, key, from_api[key])


twitch_clip_instance_helper = BasicWithId(TwitchClipInstance)


def fix_vod_and_duration(api_data):
    with db.session.begin():
        clip = get_twitch_clip_instance_by_video_id(api_data['id'])
        if clip is None:
            add_twitch_clip_instance_from_api(api_data, 'new')
            return
        clip.vod_offset = api_data['vod_offset']
        clip.duration = api_data['duration']

    db.session.flush()


def add_twitch_clip_instance_from_api(api_data, clip_type: str) -> Tuple[int, str]:
    with db.session.begin():
        if 'created_at' in api_data:
            api_data['created_at'] = isoparse(api_data['created_at'])
        log = TwitchClipInstance(api_data)
        log.type = clip_type
        db.session.add(log)
        db.session.flush()
        ret = log.id, log.broadcaster_name

    db.session.expunge(log)

    return ret


def update_twitch_clip_instance_filename(twitch_clip_id: int, file_path):
    with db.session.begin():
        item = TwitchClipInstance.query.filter_by(id=twitch_clip_id).first()
        if not item:
            return
        item.file_path = file_path

    db.session.flush()


def get_twitch_clip_instance_by_id(id: int) -> TwitchClipInstance:
    with db.session.begin():
        first = TwitchClipInstance.query.filter_by(id=id).first()
        class_dict = Dict2Class(first.to_dict())
    db.session.expunge(first)

    return class_dict
def get_twitch_clip_video_id_by_id(id: int) -> TwitchClipInstance:
    video_id = None
    with db.session.begin():
        first = TwitchClipInstance.query.filter_by(id=id).first()
        if first is not None:
            video_id = first.video_id
    db.session.expunge(first)
    return video_id

def get_twitch_clip_instance_by_video_id(video_id) -> TwitchClipInstance:
    with db.session.begin():
        first = TwitchClipInstance.query.filter_by(video_id=video_id).first()
        dict_class = Dict2Class(first.to_dict())
    return dict_class


def delete_twitch_clip_instance(instance: TwitchClipInstance):
    with db.session.begin():
        db.session.delete(instance)
    db.session.flush()
