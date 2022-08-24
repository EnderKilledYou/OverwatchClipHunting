
from typing import List

from Database.Twitch.dict_to_class import Dict2Class
from Database.Twitch.twitch_clip_tag import TwitchClipTag
from config.db_config import db


def get_tag_and_bag_by_clip_id(clip_id: int) -> List[TwitchClipTag]:
    with db.session.begin():
        items = list(list_dicts(TwitchClipTag.query.filter_by(clip_id=clip_id)))

    return items


def list_dicts(items):
    return map(lambda x: Dict2Class(x.to_dict()), items)
