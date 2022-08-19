from dateutil.parser import isoparse
from sqlalchemy_serializer import SerializerMixin

from Database.api_user import JsonFixed, FromWebDict
from config.db_config import db


class LiveTwitchInstance(db.Model, SerializerMixin, JsonFixed, FromWebDict):
    id = db.Column(db.Integer, primary_key=True)
    user_login = db.Column(db.String(90), unique=True)
    game_id = db.Column(db.String(90))
    user_name = db.Column(db.String(90))
    user_id = db.Column(db.String(90))
    game_name = db.Column(db.String(90))
    type = db.Column(db.String(20))
    _title = db.Column(db.Unicode(500))
    viewer_count = db.Column(db.Integer)
    started_at = db.Column(db.DATETIME)
    language = db.Column(db.String(10))
    thumbnail_url = db.Column(db.String(500))

    @property
    def title(self):
        return str(self._title).encode("ascii", "ignore")

    @title.setter
    def title(self, value):
        self._title = value
