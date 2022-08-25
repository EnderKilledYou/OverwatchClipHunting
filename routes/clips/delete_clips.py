from Database.Twitch.twitch_clip_instance import TwitchClipInstance
from cloud_logger import cloud_logger
from config.db_config import db
from routes.clips.clips import sharp


@sharp.function()
def deleteclips(clip_id: str):
    cloud_logger()
    with db.session.begin():
        TwitchClipInstance.query.filter_by(id=int(clip_id)).delete()

    return {"success": True}
