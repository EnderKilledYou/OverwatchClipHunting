import datetime
from typing import List

from sqlalchemy_serializer import SerializerMixin

from Database.MissingRecordError import MissingRecordError, RecordExistsError
from Database.Twitch.twitch_clip_instance_scan_job import TwitchClipInstanceScanJob, add_twitch_clip_scan
from OrmHelpers.BasicWithId import BasicWithId
from config.db_config import db


class TagClipperJob(db.Model, SerializerMixin):
    """
          a state for a clip process
      """
    serialize_rules = ()
    serialize_only = (
        'id', 'clip_id', 'tag_id', 'state', 'created_at', 'completed_at')

    id = db.Column(db.Integer, primary_key=True)
    clip_id = db.Column(db.Integer)
    tag_id = db.Column(db.Integer, unique=True)
    state = db.Column(db.Integer)
    created_at = db.Column(db.DateTime)
    completed_at = db.Column(db.DateTime)


tag_clipper_job_request_helper = BasicWithId(TagClipperJob)


def get_twitch_clip_job() -> TagClipperJob:
    with db.session.begin():
        first = TwitchClipInstanceScanJob.query.filter_by(state=0).first()
        if not first:
            return None
        first.state = 1

    db.ssession.flush()
    return first


def requeue_twitch_clip_jobs(rescanner):
    items = TwitchClipInstanceScanJob.query.filter_by(state=0)
    for item in items:
        add_twitch_clip_scan(item.clip_id,item.broadcaster)
        rescanner.add_job(item.id)


def reset_twitch_clip_job_state():
    with db.session.begin():
        items = TwitchClipInstanceScanJob.query.filter_by(state=1)
        for item in items:
            item.state = 0
        items = TwitchClipInstanceScanJob.query.filter_by(state=5)
        for item in items:
            item.state = 0

    db.session.flush()


def update_twitch_clip_job_state(job_id: int, state: int, error: str = '') -> List[TagClipperJob]:
    with db.session.begin():
        item = TwitchClipInstanceScanJob.query.filter_by(id=job_id).first()
        if not item:
            raise MissingRecordError("can't update a job i can't see")

        item.state = state

        if state == 3:
            item.error = error


    db.session.flush()


def get_twitch_clip_job_by_clip_id(clip_id: int, tag_id: int) -> TagClipperJob:
    return TwitchClipInstanceScanJob.query.filter_by(clip_id=clip_id, tag_id=tag_id).first()


def add_twitch_clip_job(clip_id: int, tag_id: int) -> TagClipperJob:
    with db.session.begin():
        exists = TagClipperJob.query.filter_by(clip_id=clip_id, tag_id=tag_id).first()
        if exists:
            raise RecordExistsError('already exists')
        log = TagClipperJob(state=0, created_at=datetime.datetime.now(), clip_id=clip_id, tag_id=tag_id)
        db.session.add(log)
    db.session.flush()
    return log
