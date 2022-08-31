import io

from PIL.Image import fromarray
from sqlalchemy_serializer import SerializerMixin

from Database.monitor import Monitor
from config.db_config import db


class MonitorLog(db.Model, SerializerMixin):
    id = db.Column(db.Integer, primary_key=True)
    monitor_id = db.Column(db.Integer, unique=True)
    text = db.Column(db.String(500), unique=True)
    event_name = db.Column(db.String(90), unique=True)
    last_image = db.Column(db.BLOB)


def update_broadcaster_log(broadcaster, text, image, event_name):
    broadcaster_id = get_monitor_id_by_broadcaster(broadcaster)
    if broadcaster_id is None:
        return
    img = fromarray(image)
    with io.BytesIO() as buf:
        img.save(buf, format="png")
        update_log(broadcaster_id, text, buf.getvalue(), event_name)
    img = None


def update_log(monitor_id, text, image, event_name):
    with db.session.begin():
        first = MonitorLog.query.filter(MonitorLog.monitor_id == monitor_id).first()
        if first is None:
            first = MonitorLog(monitor_id=monitor_id)
            db.session.add(first)

        first.text = text
        first.last_image = image
        first.event_name = event_name


def get_monitor_log_image(broadcaster: str):
    monitor_id = get_monitor_id_by_broadcaster(broadcaster)
    if monitor_id is None:
        return
    with db.session.begin():
        first = MonitorLog.query.filter(MonitorLog.monitor_id == monitor_id).first()
        if first is None:
            return None
        last_image = first.last_image

    return last_image


def get_monitor_id_by_broadcaster(broadcaster: str):
    with db.session.begin():
        item = Monitor.query.filter_by(broadcaster=broadcaster).first()
        if item is None:
            return
        _id = item.id
    return _id
