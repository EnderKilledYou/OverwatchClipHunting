from sqlalchemy_serializer import SerializerMixin

import routes.streamer
from Database.MissingRecordError import MissingRecordError
from OrmHelpers.BasicWithId import BasicWithId
from config.db_config import db


class TagAndBagRequest(db.Model, SerializerMixin):
    serialize_rules = ()
    serialize_only = (
        'id', 'clip_id', 'file_path', 'progress')
    id = db.Column(db.Integer, primary_key=True)
    clip_id = db.Column(db.Integer)
    file_path = db.Column(db.String(900), default="")

    download_progress = db.Column(db.Float, default=0)
    scan_progress = db.Column(db.Float, default=0)

    scan_error_str = db.Column(db.String(900), default="")

    scan_error = db.Column(db.Boolean, default=False)

    is_error = db.Column(db.Boolean, default=False)
    is_complete = db.Column(db.Boolean, default=False)

    cancel_request = db.Column(db.Boolean, default=False)


tag_and_bag_request_helper = BasicWithId(TagAndBagRequest)


def if_tag_and_bag_exists(clip_id: int) -> bool:
    return TagAndBagRequest.query.filter_by(clip_id=clip_id).first() is None


def if_tag_cancel_request_exists(clip_id: int) -> bool:
    first = TagAndBagRequest.query.filter_by(clip_id=clip_id).first()
    return first is not None and first.cancel_request


def update_tag_and_bag_scan_scan_error(id: int, error: str):
    bag: TagAndBagRequest = TagAndBagRequest.query.filter_by(id=id).first()
    if bag is None:
        raise MissingRecordError("Can't update non-existant bag")
        return
    bag.scan_error_str = error
    bag.scan_error = True
    bag.is_error = True
    db.session.commit()
    db.session.flush()


def update_tag_and_bag_scan_progress(id: int, progress_value: float):
    bag: TagAndBagRequest = TagAndBagRequest.query.filter_by(id=id).first()
    if bag is None:
        raise MissingRecordError("Can't update non-existant bag")
        return
    bag.scan_progress = round(progress_value, 2)
    db.session.commit()
    db.session.flush()


def add_tag_and_bag_request(clip_id: int) -> TagAndBagRequest:
    request: TagAndBagRequest = TagAndBagRequest(clip_id=clip_id)
    db.session.add(request)
    db.session.commit()
    db.session.flush()
    return request


def get_tag_and_bag_by_id(clip_id: int) -> TagAndBagRequest:
    return TagAndBagRequest.query.filter_by(clip_id=clip_id).first()
