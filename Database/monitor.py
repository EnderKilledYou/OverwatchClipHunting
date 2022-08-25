import datetime
import json

import threading
from queue import Queue
from typing import List, Dict

from oauthlib.common import generate_token
from sqlalchemy import func
from sqlalchemy.orm import validates
from sqlalchemy_serializer import SerializerMixin

from Database.Twitch.dict_to_class import Dict2Class
from Ocr.twitch_video_frame_buffer import TwitchEater

from Ocr.video_frame_buffer import VideoFrameBuffer
from cloud_logger import cloud_logger, cloud_message

from config.db_config import db

self_id = generate_token()


class Monitor(db.Model, SerializerMixin):
    def __str__(self):
        return f"Monitor {str(self.id)}  {self.broadcaster}"

    def __json__(self):
        to_dict = self.to_dict()
        return to_dict

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

    def check_need_restart(self):
        if not hasattr(self, 'ocr') or self.ocr is None:
            return
        reader = self.ocr.reader
        if not reader:
            return
        qsize = reader.count()
        frames_pending = qsize * reader.sample_every_count
        back_fill_seconds = frames_pending // reader.fps
        if back_fill_seconds <= 45:
            return
        cloud_message(f"Restarting {self.broadcaster} with backqueue of {str(back_fill_seconds)}")
        self.stop()

    ocr: VideoFrameBuffer
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
        self.get_stats = None

    def start(self):
        ocr = HeartBeatThread()
        self.get_stats = ocr.get_stats
        ocr.start(self.broadcaster)

    def stop(self):
        cloud_logger()
        if hasattr(self, 'ocr') and self.ocr is not None:
            self.ocr.stop()

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
        self.get_stats = None
        self.stop = None

    def stop(self):
        if self.stop is not None:
            self.stop()

    def start(self, broadcaster):
        cloud_logger()
        has_started = hasattr(self, 'ocr')
        if has_started:
            return
        producer_thread = threading.Thread(target=self.do_broadcast, args=[broadcaster])
        producer_thread.start()

    def do_broadcast(self, broadcaster):
        with TwitchEater(broadcaster) as ocr:
            self.stop = ocr.stop
            self.get_stats = ocr.get_stats
            ocr.buffer_broadcast()
            self.get_stats = None
            self.stop = None


def un_avoid_monitor(stream_name):
    cloud_logger()
    with db.session.begin():
        monitor = Monitor.query.filter_by(broadcaster=stream_name).first()
        if not monitor:
            return
        monitor.activated_by = ""
        monitor.is_active = True
        monitor.avoid = False


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
        last_claim_expy = time_delta.seconds > 60 * 3
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
    if hasattr(monitor, 'get_stats') and monitor.get_stats is not None:
        qsize, frames_finished, frames_finished, back_fill_seconds, fps, sample_every_count, items_read = monitor.get_stats()

        return {
            'frames_read': items_read * sample_every_count,
            'frames_done': frames_finished,
            'frames_read_seconds': frames_finished // fps,
            'back_fill_seconds': back_fill_seconds,
            'fps': fps,
            'queue_size': qsize,
            'stream_resolution': monitor.ocr.stream_res,

        }
    return default
