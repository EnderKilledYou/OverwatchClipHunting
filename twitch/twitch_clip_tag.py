from typing import List

from sqlalchemy_serializer import SerializerMixin

import routes.streamer
from twitch.twitch_clip_instance import get_twitch_clip_instance_by_id
from config.db_config import db

class TwitchClipTag(db.Model, SerializerMixin):
    serialize_rules = ()
    serialize_only = (
        'id', 'clip_id', 'tag','clip_start','clip_end','file_name','tag_amount','tag_duration')
    id = db.Column(db.Integer, primary_key=True)
    clip_created_at = db.Column(db.DateTime)
    clip_id = db.Column(db.Integer)
    tag = db.Column(db.String)
    tag_amount = db.Column(db.Integer)
    tag_duration = db.Column(db.Integer)
    tag_start = db.Column(db.Integer)
    clip_start = db.Column(db.Integer)
    clip_end = db.Column(db.Integer)
    file_name = db.Column(db.String)


def if_tag_and_bag_exists(id: int) -> bool:
    return TwitchClipTag.query.filter_by(clip_id=id).first() is None


def add_twitch_clip_tag_request(clip_id: int, tag: str, tag_amount: int, tag_duration: int,
                                tag_start: int) -> TwitchClipTag:
    clip = get_twitch_clip_instance_by_id(clip_id)
    if not clip:
        print("can add a clip tag for a clip that doesn't exist")
        return
    request: TwitchClipTag = TwitchClipTag(clip_id=clip_id, tag=tag, tag_amount=tag_amount, tag_duration=tag_duration,
                                           tag_start=tag_start, clip_created_at=clip.created_at,clip_start=tag_start,clip_end=tag_start + tag_duration)

    db.session.commit()
    db.session.flush()
    return (request, clip)


def get_tag_and_bag_by_id(id: int) -> TwitchClipTag:
    return TwitchClipTag.query.filter_by(id=id).first()


def get_tag_and_bag_by_clip_id(clip_id: int) -> List[TwitchClipTag]:
    return list(TwitchClipTag.query.filter_by(clip_id=clip_id))


def update_tag_and_bag_filename(id: int, filename_str) -> TwitchClipTag:
    item: TwitchClipTag = TwitchClipTag.query.filter_by(id=id).first()
    if not item:
        print("can't update a t and b that doesn't exist")
        return
    item.file_name = filename_str
    db.session.commit()
    db.session.flush()
    return item
