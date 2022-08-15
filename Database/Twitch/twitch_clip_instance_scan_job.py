from datetime import datetime

from sqlalchemy_serializer import SerializerMixin

from Database.Twitch.twitch_clip_instance import get_twitch_clip_instance_by_id
from Database.Twitch.twitch_clip_tag import get_tag_and_bag_by_clip_id
from OrmHelpers.BasicWithId import BasicWithId
from config.db_config import db


class TwitchClipInstanceScanJob(db.Model, SerializerMixin):
    serialize_rules = ()
    serialize_only = (
        'id', 'clip_id', 'state', 'created_at', 'completed_at', 'percent', 'error')
    id = db.Column(db.Integer, primary_key=True)
    clip_id = db.Column(db.String, unique=True)
    state = db.Column(db.Integer)
    broadcaster = db.Column(db.String)
    created_at = db.Column(db.DateTime)
    completed_at = db.Column(db.DateTime)
    percent = db.Column(db.FLOAT, default=0)
    error = db.Column(db.String, default='')


twitch_clip_instance_scan_job_helper = BasicWithId(TwitchClipInstanceScanJob)


def get_twitch_clip_scan_by_id(id: int) -> TwitchClipInstanceScanJob:
    return TwitchClipInstanceScanJob.query.filter_by(id=id).first()


def get_twitch_clip_scan_by_clip_id(clip_id: int) -> TwitchClipInstanceScanJob:
    return TwitchClipInstanceScanJob.query.filter_by(clip_id=clip_id).first()


def get_twitch_clip_scan_by_page(page: int):
    try:
        resp = TwitchClipInstanceScanJob.query.filter_by().paginate(page=page, per_page=25).items
        output = []
        for a in resp:
            by_id = get_twitch_clip_instance_by_id(a.clip_id)
            if by_id is not None:
                output.append((a, by_id))
    except:
        output = []
    return output


def add_twitch_clip_scan(clip_id: str, broadcaster: str) -> TwitchClipInstanceScanJob:
    log = get_twitch_clip_scan_by_clip_id(clip_id)
    if log:
        if log.state == 1 or log.state == 5:
            return None
        log.state = 0
        log.error = ""
        log.percent = 0
        clips_found = get_tag_and_bag_by_clip_id(clip_id)
        for a in clips_found:
            db.session.delete(a)
        db.session.commit()
        db.session.flush()

        return log
    log = TwitchClipInstanceScanJob(state=0, created_at=datetime.now(), clip_id=clip_id, broadcaster=broadcaster)
    db.session.add(log)
    db.session.commit()
    db.session.flush()
    return log


def update_scan_job_error(scan_job_id: int, error_str: str):
    item: TwitchClipInstanceScanJob = TwitchClipInstanceScanJob.query.filter_by(id=scan_job_id).first()
    if item is None:
        return
    item.state = 3
    item.error = error_str
    item.completed_at = datetime.now()
    db.session.commit()
    db.session.flush()


def update_scan_job_percent(scan_job_id: int, percent: float, is_complete: bool = False):
    item: TwitchClipInstanceScanJob = TwitchClipInstanceScanJob.query.filter_by(id=scan_job_id).first()
    if item is None:
        return
    item.percent = percent
    if item.state == 0:
        item.state = 1
    if is_complete:
        item.state = 2
        item.completed_at = datetime.now()
    db.session.commit()
    db.session.flush()


def update_scan_job_in_queue(scan_job_id: int):
    item: TwitchClipInstanceScanJob = TwitchClipInstanceScanJob.query.filter_by(id=scan_job_id).first()
    if item is None:
        return
    item.state = 5
    db.session.commit()
    db.session.flush()


def update_scan_job_started(scan_job_id: int):
    item: TwitchClipInstanceScanJob = TwitchClipInstanceScanJob.query.filter_by(id=scan_job_id).first()
    if item is None:
        return
    item.state = 1
    db.session.commit()
    db.session.flush()
    return item
