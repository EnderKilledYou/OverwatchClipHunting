from dateutil.parser import isoparse
from sqlalchemy_serializer import SerializerMixin

from OrmHelpers.BasicWithId import BasicWithId
from config.db_config import db


class TwitchUser(db.Model, SerializerMixin):
    serialize_rules = ()
    serialize_only = ('id','twitch_user_id','display_name','view_count','description' )
    id = db.Column(db.Integer, primary_key=True)
    broadcaster_type = db.Column(db.String(30))
    created_at = db.Column(db.DATETIME)
    description = db.Column(db.Unicode(900))
    display_name = db.Column(db.String(90))

    twitch_user_id = db.Column(db.String(100))
    login = db.Column(db.String(90))
    offline_image_url = db.Column(db.String(900))
    profile_image_url = db.Column(db.String(900))
    type = db.Column(db.String(90))
    view_count = db.Column(db.Integer)
    bot_token = db.Column(db.String(900))

    def __init__(self, user)  :
        self.broadcaster_type = user['broadcaster_type']
        self.created_at = isoparse (user['created_at'])
        self.description = user['description']
        self.display_name = user['display_name']
        self.twitch_user_id = user['id']
        self.login = user['login']
        self.offline_image_url = user['offline_image_url']
        self.profile_image_url = user['profile_image_url']
        self.type = user['type']
        self.view_count = user['view_count']


twitch_user_helper = BasicWithId(TwitchUser)
