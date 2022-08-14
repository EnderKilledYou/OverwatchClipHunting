from oauthlib.common import generate_token
from sqlalchemy import func
from sqlalchemy_serializer import SerializerMixin

import routes.streamer
from config.db_config import db


class BotUser(db.Model, SerializerMixin):
    serialize_rules = ()
    serialize_only = ('id', 'twitch_user_id', 'name', 'description')
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    twitch_user_id = db.Column(db.String)
    description = db.Column(db.String)
    token = db.Column(db.String)


def get_user_by_name(name, twitch_user_id):
    return BotUser.query.filter_by(name=name, twitch_user_id=twitch_user_id).first()


def get_botuser_count(twitch_user_id):
    return db.session.query(func.count(BotUser.twitch_user_id)).scalar()


def get_user_by_token(token: str):
    strip_token = token.strip()
    if len(strip_token) < 10:
        return None
    return BotUser.query.filter_by(token=strip_token).first()


def add_user_with_token(**kwargs):
    user = BotUser(kwargs)
    user.token = generate_token()

    db.session.flush()
    return user


def reset_token(user: BotUser):
    user.token = generate_token()
    db.session.commit()
    db.session.flush()


def delete_user(user: BotUser):
    db.session.delete(user)
    db.session.flush()


