from typing import List

from Database.Twitch.twitch_clip_tag import TwitchClipTag
from config.db_config import db


def get_tag_and_bag_by_clip_id(clip_id: int) -> List[TwitchClipTag]:
    with db.session.begin():
        items = list(TwitchClipTag.query.filter_by(clip_id=clip_id))
    for item in items:
        db.session.expunge(item)
    return items
