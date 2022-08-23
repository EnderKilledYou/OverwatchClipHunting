from Database.Twitch.twitch_clip_instance import TwitchClipInstance
from cloud_logger import cloud_logger
from config.db_config import db
from routes.clips.clips import sharp
from routes.query_helper import get_query_by_page


@sharp.function()
def list_twitch_clips(page: int = 1):
    cloud_logger()
    int_page = int(page)
    with db.session.begin():
        filter_by = TwitchClipInstance.query.filter_by().order_by(TwitchClipInstance.id.desc())
        clips_response = get_query_by_page(filter_by, int_page)
        tmp = []
        for clip in clips_response:
            tmp.append(clip.to_dict())


    return {"success": True, 'items': tmp}
