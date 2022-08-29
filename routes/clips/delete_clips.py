from Database.Twitch.twitch_clip_instance import TwitchClipInstance
from cloud_logger import cloud_logger
from config.db_config import db
from routes.clips.clips import sharp
from routes.login_dec import check_admin


@sharp.function()
def deleteclips(clip_id: int):
    check_admin()
    cloud_logger()
    with db.session.begin():
        TwitchClipInstance.query.filter_by(id=int(clip_id)).delete()

    return {"success": True}
