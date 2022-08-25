from Database.Twitch.twitch_clip_instance import TwitchClipInstance
from Database.Twitch.twitch_clip_instance_scan_job import TwitchClipInstanceScanJob
from config.db_config import db


def delete_clip(clip_id):

    with db.session.begin():
        first = TwitchClipInstance.query.filter_by(id=id).first()
        if first is None:
            return
        db.session.delete(first)
        scan_job = TwitchClipInstanceScanJob.query.filter_by(clip_id=id).first()
        if scan_job is not None:
            db.session.delete(scan_job)
