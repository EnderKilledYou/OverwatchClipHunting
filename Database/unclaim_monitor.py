import datetime

from Database.monitor import Monitor
from config.db_config import db


def unclaim_monitor(stream_name) -> Monitor:
    with db.session.begin():
        monitor =  Monitor.query.filter_by(broadcaster=stream_name).first()
        if monitor is None:
            return
        monitor.activated_by = ""
        monitor.activated_at = datetime.datetime(1999, 12, 11, 0, 0)
        monitor.is_active = False
    db.session.flush()
