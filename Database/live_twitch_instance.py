from sqlalchemy_serializer import SerializerMixin

from config.db_config import db


class LiveTwitchInstance(db.Model, SerializerMixin):
    id = db.Column(db.Integer, primary_key=True)
    user_login = db.Column(db.String(90), unique=True)
    game_id = db.Column(db.String(90))
    game_name = db.Column(db.String(90))
    type = db.Column(db.String(20))
    _title = db.Column(db.Unicode(500))
    viewer_count = db.Column(db.Integer)
    started_at = db.Column(db.DATETIME)
    language = db.Column(db.String(10))
    thumbnail_url = db.Column(db.String(500))

    @property
    def title(self):
        return str(self._title).lower()

    @title.setter
    def title(self, value):
        self._title = value.lower()
