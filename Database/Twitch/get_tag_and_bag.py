from typing import List

from Database.Twitch.list_dicts import list_dicts
from Database.Twitch.twitch_clip_tag import TwitchClipTag
from config.db_config import db


def get_tag_and_bag_by_clip_id(clip_id: int) -> List[TwitchClipTag]:
    with db.session.begin():
        items = list(list_dicts(TwitchClipTag.query.filter_by(clip_id=clip_id)))

    return items


def delete_tag_and_bag_by_id(id: int):
    with db.session.begin():
        TwitchClipTag.query.filter_by(id=id).delete()

def update_tag_and_bag_start_and_duration(id: int, tag_start,tag_duration) -> TwitchClipTag:
    with db.session.begin():
        item: TwitchClipTag = TwitchClipTag.query.filter_by(id=id).first()
        if not item:
            return None

        item.tag_start=tag_start
        item.tag_duration = tag_duration
        item.clip_start = tag_start
        item.clip_end = tag_start + tag_duration
        print(f"{item.tag_start} {item.tag_duration}  {item.clip_start}  {item.clip_end} ")

