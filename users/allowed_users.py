from sqlalchemy_serializer import SerializerMixin

import routes.streamer
from config.db_config import db


class AllowedUser(db.Model, SerializerMixin):
    serialize_rules = ()
    serialize_only = ('id', 'twitch_user_id', 'name', 'description')
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    twitch_user_id = db.Column(db.String)
    description = db.Column(db.String)
    disabled = db.Column(db.Boolean)


def get_user_by_name(name) -> AllowedUser:
    return AllowedUser.query.filter_by(name=name).first()


def get_user_by_twitch_id(twitch_user_id):
    return AllowedUser.query.filter_by(twitch_user_id=twitch_user_id).first()


def get_user_by_id(id: int):
    return AllowedUser.query.filter_by(id=id).first()


def update_user(user: AllowedUser, description: str):
    user.description = description
    db.session.commit()
    db.session.flush()

def update_user_setting(user: AllowedUser, description: str):
    user.description = description
    db.session.commit()
    db.session.flush()


def add_user(**kwargs):
    user = AllowedUser(kwargs)
    db.session.commit()
    db.session.flush()
    return user


def disable_user(user: AllowedUser):
    user.disabled = True
    db.session.commit()
    db.session.flush()


def delete_user(user: AllowedUser):
    db.session.delete(user)
    db.session.flush()
