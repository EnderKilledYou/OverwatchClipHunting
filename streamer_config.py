from sqlalchemy_serializer import SerializerMixin

import routes.streamer
from config.db_config import db
from routes.query_helper import get_query_by_page


class StreamerConfig(db.Model, SerializerMixin):
    serialize_rules = ()
    serialize_only = ('id', 'twitch_user_id', 'make_clips'
                      , 'min_healing_duration', 'min_elims', 'min_blocking_duration'
                      , 'min_defense_duration', 'min_assist_duration', 'stream_prefers_quality'
                      , 'clip_deaths')
    id = db.Column(db.Integer, primary_key=True)

    twitch_user_id = db.Column(db.String)
    twitch_user_name = db.Column(db.String)

    make_clips = db.Column(db.Boolean, default=True)
    min_healing_duration = db.Column(db.Integer, default=-1)
    min_elims = db.Column(db.Integer, default=-1)
    min_blocking_duration = db.Column(db.Integer, default=-1)
    min_defense_duration = db.Column(db.Integer, default=-1)
    min_assist_duration = db.Column(db.Integer, default=-1)
    stream_prefers_quality = db.Column(db.String(90), default='720p60')
    clip_deaths = db.Column(db.Boolean, default=False)


def get_config_by_twitch_id(twitch_user_id) -> StreamerConfig:
    return StreamerConfig.query.filter_by(twitch_user_id=twitch_user_id).first()


def get_config_by_id(id: int):
    return StreamerConfig.query.filter_by(id=id).first()

def get_configs(int_page: int,order_by):
    config_query_filter_by = StreamerConfig.query.filter_by()
    if order_by:
        return get_query_by_page(config_query_filter_by, int_page)
    return get_query_by_page(config_query_filter_by.order_by(StreamerConfig.id.desc()), int_page)

def get_configs_name(name_contains:str, int_page: int,order_by):
    by = StreamerConfig.query.filter_by(twitch_user_name=name_contains)
    if order_by:
        return get_query_by_page(by.order_by(StreamerConfig.twitch_user_name.asc()), int_page)
    return get_query_by_page(by.order_by(StreamerConfig.twitch_user_name.desc()), int_page)

def update_config(config: StreamerConfig, **kwargs):
    with db.session.begin():
        for key in kwargs:
            setattr(config, key, kwargs[key])
    db.session.flush()


def add_config(**kwargs):
    config = StreamerConfig(kwargs)

    db.session.flush()
    return config
