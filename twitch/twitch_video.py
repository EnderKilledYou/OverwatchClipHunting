from dateutil.parser import isoparse
from sqlalchemy_serializer import SerializerMixin

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


class TwitchVideo(db.Model, SerializerMixin):
    def AddMarker(self, marker_start, marker_end, kills, deaths, event_name):
        marker = TwitchVideoMarker(time_start=marker_start, time_end=marker_end, death_count=deaths, kill_count=kills,
                                   event_name=event_name, video_id=self.video_id, twitch_user_id=self.twitch_user_id)

        db.session.add(marker)
        db.session.commit()
        db.session.flush()

    serialize_rules = ()
    serialize_only = (
        'id', 'stream_id', 'twitch_user_id', 'user_name', 'description', 'title', 'url', 'thumbnail_url', 'viewable',
        'view_count',
        'duration')
    id = db.Column(db.Integer, primary_key=True)
    video_id = db.Column(db.Integer,unique=True)
    stream_id: None
    twitch_user_id = db.Column(db.String)
    user_login = db.Column(db.String)
    user_name = db.Column(db.String)
    title = db.Column(db.String)
    description = db.Column(db.String)
    created_at = db.Column(db.DATETIME)
    published_at = db.Column(db.DATETIME)
    url = db.Column(db.String)
    thumbnail_url = db.Column(db.String)
    viewable = db.Column(db.String)
    view_count = db.Column(db.Integer)
    language = db.Column(db.String)
    type = db.Column(db.String)
    duration = db.Column(db.String)
    percent_done = db.Column(db.Integer)
    started_on = db.Column(db.DATETIME)
    finished_on = db.Column(db.DATETIME)
    errors = db.Column(db.String)

    def __init__(self, video) -> None:
        self.percent_done = 0
        self.video_id = video['id']
        self.stream_id = video['stream_id']
        self.user_id = video['user_id']
        self.user_login = video['user_login']
        self.user_name = video['user_name']
        self.title = video['title']
        self.description = video['description']
        self.created_at =  isoparse (video['created_at'])
        self.published_at = isoparse (video['published_at'])
        self.url = video['url']
        self.thumbnail_url = video['thumbnail_url']
        self.viewable = video['viewable']
        self.view_count = video['view_count']
        self.language = video['language']
        self.type = video['type']
        self.duration = video['duration']
