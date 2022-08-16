from dateutil.parser import isoparse
from sqlalchemy_serializer import SerializerMixin

from OrmHelpers.BasicWithId import BasicWithId
from config.db_config import db


class TwitchClipInstance(db.Model, SerializerMixin):
    serialize_rules = ()
    serialize_only = (
        'id', 'video_id', 'video_url', 'created_at', 'thumbnail_url',
        'title', 'broadcaster_name', 'type', 'vod_offset', 'duration')
    id = db.Column(db.Integer, primary_key=True)
    video_id = db.Column(db.String, unique=True)
    video_url = db.Column(db.String, unique=True)
    created_at = db.Column(db.DateTime)
    thumbnail_url = db.Column(db.String)
    title = db.Column(db.String)
    broadcaster_name = db.Column(db.String)
    type = db.Column(db.String)
    vod_offset = db.Column(db.Integer)
    duration = db.Column(db.Integer)
    file_path = db.Column(db.String)

    def __init__(self, from_api={}):
        if 'id' in from_api:
            from_api['video_id'] = from_api['id']
            from_api.pop('id')
        for key in from_api:
            setattr(self, key, from_api[key])


twitch_clip_instance_helper = BasicWithId(TwitchClipInstance)


def fix_vod_and_duration(api_data):
    clip = get_twitch_clip_instance_by_video_id(api_data['id'])
    if clip is None:
        add_twitch_clip_instance_from_api(api_data, 'new')
        return
    clip.vod_offset = api_data['vod_offset']
    clip.duration = api_data['duration']
    db.session.commit()
    db.session.flush()


def add_twitch_clip_instance_from_api(api_data, clip_type: str) -> TwitchClipInstance:
    if 'created_at' in api_data:
        api_data['created_at'] = isoparse(api_data['created_at'])
    log = TwitchClipInstance(api_data)
    log.type = clip_type
    db.session.add(log)
    db.session.commit()
    db.session.flush()
    return log


def update_twitch_clip_instance_filename(twitch_clip_id: int, file_path):
    item = get_twitch_clip_instance_by_id(twitch_clip_id)
    if not item:
        return
    item.file_path = file_path
    db.session.commit()
    db.session.flush()

def get_twitch_clip_instance_by_id(id: int) -> TwitchClipInstance:
    return TwitchClipInstance.query.filter_by(id=id).first()


def get_twitch_clip_instance_by_video_id(video_id) -> TwitchClipInstance:
    return TwitchClipInstance.query.filter_by(video_id=video_id).first()


def delete_twitch_clip_instance(instance: TwitchClipInstance):
    db.session.delete(instance)
    db.session.commit()
    db.session.flush()
