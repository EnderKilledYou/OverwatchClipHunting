from dateutil.parser import isoparse
from sqlalchemy_serializer import SerializerMixin

from Database.api_user import JsonFixed, FromWebDict
from config.db_config import db


class LiveTwitchInstance(SerializerMixin, JsonFixed, FromWebDict):
    serialize_rules = ()
    serialize_only = (
        'id', 'user_login', 'game_id', 'user_name', 'user_id',
        'game_name', 'type', 'type', 'title', 'viewer_count', 'started_at', 'language', 'thumbnail_url')
    id: int
    user_login: str
    game_id: str
    user_name: str
    user_id: str
    game_name: str
    type: str
    title: str
    viewer_count: str
    started_at: str
    language: str
    thumbnail_url: str

    def __init__(self, args):
        self.id = 0
        self.user_login=None
        self.game_id=None
        self.user_name=None
        self.user_id=None
        self.game_name=None
        self.type=None
        self.title=None
        self.viewer_count=None
        self.started_at=None
        self.language=None
        self.thumbnail_url=None
        self.from_web(args)

