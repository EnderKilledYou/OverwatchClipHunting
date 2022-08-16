from typing import List

from Database.Twitch.twitch_clip_tag import TwitchClipTag


def get_tag_and_bag_by_clip_id(clip_id: int) -> List[TwitchClipTag]:
    return list(TwitchClipTag.query.filter_by(clip_id=clip_id))
