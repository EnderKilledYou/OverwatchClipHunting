

from Database.monitor import Monitor
from cloud_logger import cloud_logger
from config.db_config import db


def avoid_monitor(stream_name):
    cloud_logger()
    with db.session.begin():
        monitor = Monitor.query.filter_by(broadcaster=stream_name).first()
        if not monitor:
            return
        monitor.activated_by = "<avoid>"
        monitor.avoid = True



