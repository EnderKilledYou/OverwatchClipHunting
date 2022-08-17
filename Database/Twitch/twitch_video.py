from dateutil.parser import isoparse
from sqlalchemy_serializer import SerializerMixin

from OrmHelpers.BasicWithId import BasicWithId
from config.db_config import db


class TwitchVideo(db.Model, SerializerMixin):


    serialize_rules = ()
    serialize_only = (
        'id', 'stream_id', 'twitch_user_id', 'user_name', 'description', 'title', 'url', 'thumbnail_url', 'viewable',
        'view_count',
        'duration')
    id = db.Column(db.Integer, primary_key=True)
    video_id = db.Column(db.Integer, unique=True)
    stream_id: None
    twitch_user_id = db.Column(db.String(90))
    user_login = db.Column(db.String(90))
    user_name = db.Column(db.String(90))
    title = db.Column(db.Unicode(900))
    description = db.Column(db.Unicode(900))
    created_at = db.Column(db.DATETIME)
    published_at = db.Column(db.DATETIME)
    url = db.Column(db.String(900))
    thumbnail_url = db.Column(db.String(900))
    viewable = db.Column(db.String(900))
    view_count = db.Column(db.Integer)
    language = db.Column(db.String(20))
    type = db.Column(db.String(90))
    duration = db.Column(db.Integer)
    percent_done = db.Column(db.Integer)
    started_on = db.Column(db.DATETIME)
    finished_on = db.Column(db.DATETIME)
    errors = db.Column(db.String(900))

    def __init__(self, video) -> None:
        self.percent_done = 0
        self.video_id = video['id']
        self.stream_id = video['stream_id']
        self.user_id = video['user_id']
        self.user_login = video['user_login']
        self.user_name = video['user_name']
        self.title = video['title']
        self.description = video['description']
        self.created_at = isoparse(video['created_at'])
        self.published_at = isoparse(video['published_at'])
        self.url = video['url']
        self.thumbnail_url = video['thumbnail_url']
        self.viewable = video['viewable']
        self.view_count = video['view_count']
        self.language = video['language']
        self.type = video['type']
        self.duration = video['duration']

twitch_video_helper = BasicWithId(TwitchVideo)