from sqlalchemy_serializer import SerializerMixin

from OrmHelpers.BasicWithId import BasicWithId
from config.db_config import db


class TwitchVideoMarker(db.Model, SerializerMixin):
    serialize_rules = ()
    serialize_only = (
        'id',)
    id = db.Column(db.Integer, primary_key=True)
    twitch_user_id = db.Column(db.Integer)
    video_id = db.Column(db.Integer)
    time_start = db.Column(db.Integer)
    time_end = db.Column(db.Integer)
    death_count = db.Column(db.Integer)
    kill_count = db.Column(db.Integer)
    heal_count = db.Column(db.Integer)
    event_name = db.Column(db.String)  # kill, map start, etc


twitch_video_marker_helper = BasicWithId(TwitchVideoMarker)
