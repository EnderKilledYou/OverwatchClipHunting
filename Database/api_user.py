from oauthlib.common import generate_token
from sqlalchemy import func
from sqlalchemy_serializer import SerializerMixin

import routes.streamer
from config.db_config import db


class ApiUser(db.Model, SerializerMixin):
    serialize_rules = ()
    serialize_only = ('id', 'twitch_user_id', 'name', 'description')
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    twitch_user_id = db.Column(db.String)
    description = db.Column(db.String)
    token = db.Column(db.String)


def get_user_by_name(name, twitch_user_id):
    return ApiUser.query.filter_by(name=name, twitch_user_id=twitch_user_id).first()


def get_subuser_count(twitch_user_id):
    return db.session.query(func.count(ApiUser.twitch_user_id)).scalar()


def get_user_by_token(token: str):
    strip_token = token.strip()
    if len(strip_token) < 10:
        return None
    return ApiUser.query.filter_by(token=strip_token).first()


def add_user_with_token(**kwargs):
    user = ApiUser(kwargs)
    user.token = generate_token()
    db.session.add(user)
    db.session.flush()
    return user


def reset_token(user: ApiUser):
    user.token = generate_token()
    db.session.commit()
    db.session.flush()


def delete_user(user: ApiUser):
    db.session.delete(user)
    db.session.flush()
