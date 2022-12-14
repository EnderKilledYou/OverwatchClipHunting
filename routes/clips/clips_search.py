from typing import List

from Database.Twitch.twitch_clip_instance import TwitchClipInstance
from Database.Twitch.twitch_clip_tag import TwitchClipTag
from cloud_logger import cloud_logger
from config.db_config import db
from routes.clips.clips import sharp
from routes.login_dec import check_admin


@sharp.function()
def clips_search(creator_name: str, clip_type: List[str] = [], duration_min: int = 0, page: int = 1):
    cloud_logger()
    check_admin()
    int_page = int(page)
    if int_page < 1:
        int_page = 1
    with db.session.begin():
        q = TwitchClipInstance.query.join(TwitchClipTag,
                                          TwitchClipInstance.id == TwitchClipTag.clip_id, isouter=False).with_entities(
            TwitchClipInstance, TwitchClipTag)

        if len(clip_type) > 0:
            q = q.filter(TwitchClipTag.tag.in_(clip_type))
        if duration_min > 0:
            q = q.filter(TwitchClipTag.tag_duration >= duration_min)

        if len(creator_name) > 0:
            q = q.filter(TwitchClipInstance.broadcaster_name == creator_name)

        clip_dict = {}
        for a in q.order_by(TwitchClipInstance.id.desc()).limit(100).offset((int_page - 1) * 100):
            if a[1] is None:
                continue
            if a[0] not in clip_dict:
                clip_dict[a[0]] = (a[0].to_dict(), [])
            clip_dict[a[0]][1].append(a[1].to_dict())

    return {"success": True, 'items': list(clip_dict.values())}
