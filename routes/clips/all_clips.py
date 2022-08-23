from Database.Twitch.dict_to_class import Dict2Class
from Database.Twitch.get_tag_and_bag import get_tag_and_bag_by_clip_id
from Database.Twitch.twitch_clip_instance import TwitchClipInstance
from cloud_logger import cloud_logger
from config.db_config import db
from routes.clips.clips import sharp
from routes.query_helper import get_query_by_page
from routes.utils import query_to_list


@sharp.function()
def all_clips(clip_type: str = "", page: int = 1):
    cloud_logger()
    int_page = int(page)
    with db.session.begin():
        if clip_type == "all":
            filter_by = TwitchClipInstance.query.filter_by()  # .order_by(TwitchClipLog.id.desc())
        else:
            filter_by = TwitchClipInstance.query.filter_by(type=clip_type).order_by(TwitchClipInstance.id.desc())

        clips_response = get_query_by_page(filter_by, int_page)

        clip_list = query_to_list(clips_response)
        resp_list = []
    for clip in clip_list:

        tags = list(map(lambda x: x.to_dict(), get_tag_and_bag_by_clip_id(clip['id'])))
        resp_list.append((Dict2Class(clip.to_dict()), tags))
    return {"success": True, 'items': resp_list}
