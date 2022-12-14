import datetime
import json
import os.path

from typing import List, Dict
from oauthlib.common import generate_token
from sqlalchemy import func
from sqlalchemy.orm import validates
from sqlalchemy_serializer import SerializerMixin
from Database.Twitch.dict_to_class import Dict2Class
from cloud_logger import cloud_logger, cloud_message
from config.db_config import db

if not os.path.exists('id.txt'):
    self_id = generate_token()
    with open('id.txt', 'w') as id_file:
        id_file.write(self_id)
else:
    with open('id.txt', 'r') as id_file:
        self_id = id_file.read().strip()


class Monitor(db.Model, SerializerMixin):
    def __str__(self):
        return f"Monitor {str(self.id)}  {self.broadcaster}"

    def __json__(self):
        to_dict = self.to_dict()
        return to_dict

    def get_stats(self):
        if self._get_stats is not None:
            return self._get_stats()

    @validates('broadcaster')
    def name_to_lower(self, key, value):
        return value.lower()

    @property
    def Broadcaster(self):
        return self.broadcaster.lower()

    def __repr__(self):
        try:
            return json.dumps(self.to_dict())
        except:
            print("Monitor convert to json failed")
            return str(self.to_dict())


    broadcaster: str

    serialize_rules = ()
    serialize_only = ('id', 'activated_by', 'broadcaster', 'make_clips'
                      , 'min_healing_duration', 'min_elims', 'min_blocking_duration'
                      , 'min_defense_duration', 'min_assist_duration', 'stream_prefers_quality'
                      , 'clip_deaths', 'is_active', 'activated_at', 'activated_by',
                      'last_check_in', 'avoid', 'cancel_request',
                      'frames_read', 'frames_done', 'frames_read_seconds',
                      'back_fill_seconds', 'fps', 'queue_size',
                      'stream_resolution')
    id = db.Column(db.Integer, primary_key=True)
    broadcaster = db.Column(db.String(90), unique=True)
    make_clips = db.Column(db.Boolean, default=True)
    min_healing_duration = db.Column(db.Integer, default=-1)
    min_elims = db.Column(db.Integer, default=-1)
    min_blocking_duration = db.Column(db.Integer, default=-1)
    min_defense_duration = db.Column(db.Integer, default=-1)
    min_assist_duration = db.Column(db.Integer, default=-1)
    stream_prefers_quality = db.Column(db.String(90), default='720p60')
    clip_deaths = db.Column(db.Boolean, default=False)
    is_active = db.Column(db.Boolean, default=True)
    activated_at = db.Column(db.DATETIME, default=datetime.datetime(1999, 12, 11, 0, 0))
    activated_by = db.Column(db.String(30))
    last_check_in = db.Column(db.DATETIME)
    avoid = db.Column(db.Boolean(), default=False)
    cancel_request = db.Column(db.Boolean, default=True)
    frames_read = db.Column(db.Integer, default=-1)
    frames_done = db.Column(db.Integer, default=-1)
    frames_read_seconds = db.Column(db.Integer, default=-1)
    back_fill_seconds = db.Column(db.Integer, default=-1)
    fps = db.Column(db.Integer, default=-1)
    queue_size = db.Column(db.Integer, default=-1)
    stream_resolution = db.Column(db.String(30))

    def __init__(self, broadcaster: str, web_dict={}):
        self.broadcaster = broadcaster
        self.web_dict = web_dict
        self._get_stats = None
        self._stop = None

    def stop(self):
        cloud_logger()
        print(f"stopping... monitor stopping {self.broadcaster}")
        if self._stop is not None:
            print(f"stopping... calling stop on monitor stopping {self.broadcaster}")
            self._stop()

    def wait_for_stop(self, timeout=None):
        cloud_logger()
        self.producer_thread.join(timeout)


def add_stream_to_monitor(broadcaster: str):
    cloud_logger()
    with db.session.begin():
        lower = broadcaster.lower().strip()
        exists = get_monitor_exists(lower)
        if exists == 0:
            monitor2 = Monitor(lower)
            monitor2.is_active = True
            db.session.add(monitor2)
            return True

    un_avoid_monitor(lower)
    return True


class HeartBeatThread:
    def __init__(self):
        self._get_stats = None
        self._stop = None

    def get_stats(self):
        if self._get_stats is not None:
            return self._get_stats()
        return None

    def stop(self):
        if self._stop is not None:
            self._stop()


def un_avoid_monitor(stream_name):
    cloud_logger()
    with db.session.begin():
        monitor = Monitor.query.filter_by(broadcaster=stream_name).first()
        if not monitor:
            return
        monitor.activated_by = ""
        monitor.is_active = True
        monitor.avoid = False


def update_monitor_stats(broadcaster, stats: Dict[str, any]):
    items_out = []
    # cloud_logger()
    with db.session.begin():
        item = Monitor.query.filter_by(broadcaster=broadcaster).first()
        if item is None:
            return
        for attr in stats:
            if hasattr(item, attr):
                setattr(item, attr, stats[attr])




def get_all_monitors_dicts() -> List[Dict[str, any]]:
    items_out = []
    # cloud_logger()
    with db.session.begin():
        items = list(Monitor.query.filter_by(avoid=False))
        for item in items:
            items_out.append(item.to_dict())
    return items_out


def get_all_monitors() -> List[Monitor]:
    items_out = []
    # cloud_logger()
    with db.session.begin():
        items = list(Monitor.query.filter_by(avoid=False))
        for item in items:
            items_out.append(Dict2Class(item.to_dict()))
    return items_out


def get_all_logins() -> List[str]:
    # cloud_logger()
    with db.session.begin():
        return list(map(lambda a: a[0], db.session.query(Monitor.broadcaster).filter_by(avoid=False)))


def get_inactive_monitors() -> List[Monitor]:
    cloud_logger()
    return list(Monitor.query.filter_by(is_active=False, avoid=False))


def get_all_my_monitors() -> List[Monitor]:
    cloud_logger()
    with db.session.begin():
        return list(map(lambda x: Dict2Class(x.to_dict()), Monitor.query.filter_by(activated_by=self_id)))


def get_all_my_monitors_names() -> List[Monitor]:
    cloud_logger()
    with db.session.begin():
        return list(db.session.query(Monitor.broadcaster).filter_by(activated_by=self_id))


class NotOursAnymoreError:
    pass


def update_claim_on_monitor(stream_name, fields: Dict[str, any] = {}) -> Monitor:
    with db.session.begin():
        monitor = Monitor.query.filter_by(broadcaster=stream_name).first()
        if monitor is None or monitor.activated_by != self_id:
            return False

        monitor.activated_at = datetime.datetime.now()
        for field_name in fields:
            setattr(monitor, field_name, fields[field_name])

    return True


def get_claimed_count() -> Monitor:
    with db.session.begin():
        return db.session.query(func.count(Monitor.id)).filter_by(activated_by=self_id).scalar()


def reset_for_claim(stream_name):
    with db.session.begin():
        monitor = Monitor.query.filter_by(broadcaster=stream_name).first()
        if monitor is None:
            return
        monitor.frames_read = 0
        monitor.frames_done = 0
        monitor.frames_read_seconds = 0
        monitor.back_fill_seconds = 0
        monitor.fps = 0
        monitor.queue_size = 0
        monitor.stream_resolution = ''


def release_monitors() -> bool:
    cloud_logger()
    with db.session.begin():
        minutes_in_past = datetime.datetime.now() - datetime.timedelta(minutes=5)
        query = Monitor.query.filter(
            Monitor.activated_at < minutes_in_past)
        update_values = {
            Monitor.activated_by: '',
            Monitor.is_active: False
        }
        return query.update(update_values)


def claim_monitor(stream_name) -> bool:
    cloud_logger()
    with db.session.begin():
        current_time = datetime.datetime.now()
        monitor = Monitor.query.filter_by(broadcaster=stream_name).first()
        if monitor is None:
            cloud_message("Could not import " + stream_name + " when looking at streamers")
            return False
        if monitor.activated_by == self_id:
            return False
        time_delta = current_time - datetime.datetime(1999, 12, 11, 0, 0)
        if monitor.activated_at is not None:
            time_delta = current_time - monitor.activated_at
        last_claim_expy = time_delta.seconds > 60
        if last_claim_expy or not monitor.is_active:
            query = Monitor.query.filter_by(
                activated_by=monitor.activated_by, broadcaster=stream_name)
            update_values = {
                Monitor.activated_by: self_id,
                Monitor.activated_at: current_time,
                Monitor.is_active: True}
            result = query.update(update_values
                                  , synchronize_session=False)

            return result == 1
        return False


def assert_monitor_still_claimed(monitor_id: str):
    cloud_logger()
    return Monitor.query.filter_by(id=monitor_id, activated_by=self_id).first()


def get_my_inactive_monitors() -> List[Monitor]:
    cloud_logger()
    return list(Monitor.query.filter_by(is_active=False, activated_by=self_id))


def get_my_active_monitors() -> List[Monitor]:
    cloud_logger()
    return list(Monitor.query.filter_by(is_active=True, activated_by=self_id))


def get_active_monitors() -> List[Monitor]:
    cloud_logger()
    return list(Monitor.query.filter_by(is_active=True))


def get_active_monitors_names() -> List[Monitor]:
    cloud_logger()
    filter_by = db.session.query(Monitor.broadcaster).filter_by(is_active=True).all()

    return list(map(lambda x: x[0], filter_by))


def get_monitor_by_id(monitor_id: int) -> Monitor:
    cloud_logger()
    return Monitor.query.filter_by(id=monitor_id).first()


def get_monitor_by_name(stream_name: str) -> Monitor:
    cloud_logger()
    with db.session.begin():
        item = Monitor.query.filter_by(broadcaster=stream_name).first()
        if item is None:
            return None
        dict = item.to_dict()
        db.session.expunge(item)
    return item


def get_monitor_exists(stream_name: str) -> Monitor:
    cloud_logger()
    return Monitor.query.filter_by(broadcaster=stream_name).count()


def cancel_stream_to_monitor(stream_name):
    cloud_logger()
    with db.session.begin():
        monitor = get_monitor_by_name(stream_name)
        if not monitor:
            return
        monitor.cancel_request = True


def remove_stream_to_monitor(stream_name):
    with db.session.begin():
        monitor = get_monitor_by_name(stream_name)
        if not monitor:
            return
        monitor.is_active = False


default = {

    'frames_read': 0,
    'frames_done': 0,
    'frames_read_seconds': 0,
    'back_fill_seconds': 0,
    'fps': 0,
    'queue_size': 0,
    'stream_resolution': '',

}


def get_monitor_stats(monitor: Monitor) -> Dict[str, str]:
    if hasattr(monitor, '_get_stats') and monitor._get_stats is not None:
        item = monitor.get_stats()
        if item is None or len(item) != 8:
            return default
        qsize, frames_finished, frames_finished, back_fill_seconds, fps, sample_every_count, items_read, stream_res = item
        return {
            'frames_read': items_read * sample_every_count,
            'frames_done': frames_finished,
            'frames_read_seconds': frames_finished // fps,
            'back_fill_seconds': back_fill_seconds,
            'fps': fps,
            'queue_size': qsize,
            'stream_resolution': stream_res,

        }
    return default


from sqlalchemy import event


@event.listens_for(Monitor, 'load')
def receive_load(target, context):
    target._get_stats = None
    target._stop = None
