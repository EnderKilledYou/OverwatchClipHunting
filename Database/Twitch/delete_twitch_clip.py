from Database.Twitch.twitch_clip_instance import TwitchClipInstance
from Database.Twitch.twitch_clip_instance_scan_job import TwitchClipInstanceScanJob
from config.db_config import db


def delete_clip(clip_id):
    with db.session.begin():
        TwitchClipInstance.query.filter(TwitchClipInstance.id == clip_id).delete()
        TwitchClipInstanceScanJob.query.filter(TwitchClipInstanceScanJob.clip_id == clip_id).delete()
