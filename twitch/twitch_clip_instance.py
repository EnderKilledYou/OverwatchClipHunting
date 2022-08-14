import datetime
from typing import List

from dateutil.parser import isoparse
from sqlalchemy_serializer import SerializerMixin

import routes.streamer
from config.db_config import db


class TagClipperJob(db.Model, SerializerMixin):
    serialize_rules = ()
    serialize_only = (
        'id', 'clip_id', 'tag_id', 'state', 'created_at', 'completed_at')

    id = db.Column(db.Integer, primary_key=True)
    clip_id = db.Column(db.String)
    tag_id = db.Column(db.String, unique=True)
    state = db.Column(db.Integer)
    created_at = db.Column(db.DateTime)
    completed_at = db.Column(db.DateTime)


def get_twitch_clip_job() -> TagClipperJob:
    first = TwitchClipInstanceScanJob.query.filter_by(state=0).first()
    if not first:
        return None
    first.state = 1
    db.session.commit()
    db.session.flush()
    return first


def reset_twitch_clip_job_state():
    items = TwitchClipInstanceScanJob.query.filter_by(state=1)
    for item in items:
        item.state = 0
    db.session.commit()
    db.session.flush()


def update_twitch_clip_job_state(job_id: int, state: int, error: str = '') -> List[TagClipperJob]:
    item = TwitchClipInstanceScanJob.query.filter_by(id=job_id).first()
    if not item:
        print("can't update a job i can't see")
        return
    item.state = state

    if state == 3:
        item.error = error

    db.session.commit()
    db.session.flush()


def get_twitch_clip_job_by_clip_id(clip_id: int, tag_id: int) -> TagClipperJob:
    return TwitchClipInstanceScanJob.query.filter_by(clip_id=clip_id, tag_id=tag_id).first()


def add_twitch_clip_job(clip_id: int, tag_id: int) -> TagClipperJob:
    exists = TagClipperJob.query.filter_by(clip_id=clip_id, tag_id=tag_id).first()
    if exists:
        print('already exists')
        return exists
    log = TagClipperJob(state=0, created_at=datetime.datetime.now(), clip_id=clip_id, tag_id=tag_id)

    db.session.commit()
    db.session.flush()
    return log


class TwitchClipInstanceScanJob(db.Model, SerializerMixin):
    serialize_rules = ()
    serialize_only = (
        'id', 'clip_id', 'state', 'created_at', 'completed_at')
    id = db.Column(db.Integer, primary_key=True)
    clip_id = db.Column(db.String, unique=True)
    state = db.Column(db.Integer)
    created_at = db.Column(db.DateTime)
    completed_at = db.Column(db.DateTime)
    error = db.Column(db.String, default='')


def get_twitch_clip_scan_by_clip_id(clip_id: int) -> TwitchClipInstanceScanJob:
    return TwitchClipInstanceScanJob.query.filter_by(clip_id=clip_id).first()


def add_twitch_clip_scan(clip_id: str) -> TwitchClipInstanceScanJob:
    log = get_twitch_clip_scan_by_clip_id(clip_id)
    if log:
        log.state = 0
        print("exists")

    else:
        log = TwitchClipInstanceScanJob(state=0, created_at=datetime.datetime.now(), clip_id=clip_id)

    db.session.commit()
    db.session.flush()
    return log


class TwitchClipInstance(db.Model, SerializerMixin):
    serialize_rules = ()
    serialize_only = (
        'id', 'video_id', 'video_url', 'created_at', 'thumbnail_url',
        'title', 'broadcaster_name', 'type')
    id = db.Column(db.Integer, primary_key=True)
    video_id = db.Column(db.String, unique=True)
    video_url = db.Column(db.String, unique=True)
    created_at = db.Column(db.DateTime)
    thumbnail_url = db.Column(db.String)
    title = db.Column(db.String)
    broadcaster_name = db.Column(db.String)
    type = db.Column(db.String)

    def __init__(self, from_api={}):
        if 'id' in from_api:
            from_api['video_id'] = from_api['id']
            from_api.pop('id')
        for key in from_api:
            setattr(self, key, from_api[key])


def add_twitch_clip_instance_from_api(api_data, clip_type: str):
    if 'created_at' in api_data:
        api_data['created_at'] = isoparse(api_data['created_at'])
    log = TwitchClipInstance(api_data)
    log.type = clip_type

    db.session.commit()
    db.session.flush()
    return log


def get_twitch_clip_instance_by_id(id: int) -> TwitchClipInstance:
    return TwitchClipInstance.query.filter_by(id=id).first()


def get_twitch_clip_instance_by_video_id(video_id) -> TwitchClipInstance:
    return TwitchClipInstance.query.filter_by(video_id=video_id).first()


def delete_twitch_clip_instance(instance: TwitchClipInstance):
    db.session.delete(instance)
    db.session.commit()
    db.session.flush()
