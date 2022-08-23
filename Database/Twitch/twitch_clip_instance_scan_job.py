from datetime import datetime
from enum import IntEnum

from sqlalchemy_serializer import SerializerMixin

from Database.Twitch.dict_to_class import Dict2Class
from Database.Twitch.twitch_clip_tag import TwitchClipTag
from config.db_config import db


class TwitchClipJobState(IntEnum):
    Complete = 2
    InQueue = 0
    DownloadingClip = 1
    Error = 3
    InQueueForTag = 5
    Scanning = 6
    Yielding = 7
    DeepFacing = 8
    DeepFacingQueue =9


class TwitchClipInstanceScanJob(db.Model, SerializerMixin):
    serialize_rules = ()
    serialize_only = (
        'id', 'clip_id', 'state', 'created_at', 'completed_at', 'percent', 'error', 'broadcaster')
    id = db.Column(db.Integer, primary_key=True)
    clip_id = db.Column(db.String(90), unique=True)
    state = db.Column(db.Integer)
    broadcaster = db.Column(db.String(90))
    created_at = db.Column(db.DateTime)
    completed_at = db.Column(db.DateTime)
    percent = db.Column(db.FLOAT, default=0)
    error = db.Column(db.String(900), default='')


from Database.Twitch.twitch_clip_instance import get_twitch_clip_instance_by_id, TwitchClipInstance

from OrmHelpers.BasicWithId import BasicWithId

twitch_clip_instance_scan_job_helper = BasicWithId(TwitchClipInstanceScanJob)


def get_twitch_clip_scan_by_id(id: int) -> TwitchClipInstanceScanJob:
    with db.session.begin():
        first = TwitchClipInstanceScanJob.query.filter_by(id=id).first()
        logclass = Dict2Class(first.to_dict())
    return logclass


def get_twitch_clip_scan_by_clip_id(clip_id: int) -> TwitchClipInstanceScanJob:
    with db.session.begin():
        first = TwitchClipInstanceScanJob.query.filter_by(clip_id=clip_id).first()
        logclass = Dict2Class(first.to_dict())
    return logclass


def get_twitch_clip_scan_by_page(page: int, page_count: int = 25):
    output = []
    with db.session.begin():
        resp = TwitchClipInstanceScanJob.query.filter_by().order_by(TwitchClipInstanceScanJob.id.desc()).paginate(
            page=page, per_page=page_count).items
    for a in resp:
        by_id = TwitchClipInstance.query.filter_by(id=a.clip_id).first()
        if by_id is not None:
            output.append((a.to_dict(), by_id.to_dict()))

    return output


def add_twitch_clip_scan(clip_id: str, broadcaster: str) -> TwitchClipInstanceScanJob:
    with db.session.begin():
        log = TwitchClipInstanceScanJob.query.filter_by(clip_id=clip_id).first()
        if log:
            if log.state == 1 or log.state == 5:
                return None
            db.session.delete(log)
        clips_found = list(TwitchClipTag.query.filter_by(clip_id=clip_id))
        for a in clips_found:
            db.session.delete(a)
        log = TwitchClipInstanceScanJob(state=0, created_at=datetime.now(), clip_id=clip_id, broadcaster=broadcaster)
        db.session.add(log)
        db.session.flush()
        id = log.id


    return id


def update_scan_job_error(scan_job_id: int, error_str: str):
    with db.session.begin():
        item: TwitchClipInstanceScanJob = TwitchClipInstanceScanJob.query.filter_by(id=scan_job_id).first()
        if item is None:
            return
        item.state = 3
        item.error = error_str
        item.completed_at = datetime.now()
    db.session.flush()


def update_scan_job_percent(scan_job_id: int, percent: float, is_complete: bool = False):
    with db.session.begin():
        item: TwitchClipInstanceScanJob = TwitchClipInstanceScanJob.query.filter_by(id=scan_job_id).first()
        if item is None:
            return
        item.percent = percent
        if item.state == TwitchClipJobState.InQueue:
            item.state = TwitchClipJobState.DownloadingClip
        if is_complete:
            item.state = TwitchClipJobState.Complete
            item.completed_at = datetime.now()

    db.session.flush()


def update_scan_job_in_scanning(scan_job_id: int):
    with db.session.begin():
        item: TwitchClipInstanceScanJob = TwitchClipInstanceScanJob.query.filter_by(id=scan_job_id).first()
        if item is None:
            return
        item.state = TwitchClipJobState.Scanning
    db.session.flush()


def update_scan_job_in_subclip(scan_job_id: int):
    with db.session.begin():
        item: TwitchClipInstanceScanJob = TwitchClipInstanceScanJob.query.filter_by(id=scan_job_id).first()
        if item is None:
            return
        item.state = TwitchClipJobState.Yielding
    db.session.flush()


def update_scan_job_in_deepface(scan_job_id: int):
    with db.session.begin():
        item: TwitchClipInstanceScanJob = TwitchClipInstance.query.filter_by(id=scan_job_id).first()
        if item is None:
            return
        item.state = TwitchClipJobState.DeepFacing
        item.percent = 0
    db.session.flush()
def update_scan_job_in_deepfacequeue(scan_job_id: int):
    with db.session.begin():
        item: TwitchClipInstanceScanJob = TwitchClipInstance.query.filter_by(id=scan_job_id).first()
        if item is None:
            return
        item.state = TwitchClipJobState.DeepFacingQueue
        item.percent = 0
    db.session.flush()


def update_scan_job_started(scan_job_id: int):
    with db.session.begin():
        item: TwitchClipInstanceScanJob = TwitchClipInstanceScanJob.query.filter_by(id=scan_job_id).first()
        if item is None:
            return
        item.state = 1
        item.percent = 0
        dict_class = Dict2Class(item.to_dict())
    db.session.flush()

    return dict_class
