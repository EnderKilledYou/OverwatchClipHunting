
from typing import List

from Database.Twitch.list_dicts import list_dicts
from Database.Twitch.twitch_clip_tag import TwitchClipTag
from config.db_config import db


def get_tag_and_bag_by_clip_id(clip_id: int) -> List[TwitchClipTag]:
    with db.session.begin():
        items = list(list_dicts(TwitchClipTag.query.filter_by(clip_id=clip_id)))

    return items


