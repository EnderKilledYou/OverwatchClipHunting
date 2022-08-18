import datetime
import json
import threading
from queue import Queue
from typing import List

from oauthlib.common import generate_token
from sqlalchemy_serializer import SerializerMixin

from Ocr.overwatch_screen_reader import OverwatchScreenReader
from Ocr.screen_reader import ScreenReader
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

    def __repr__(self):
        try:
            return json.dumps(self.to_dict())
        except:
            print("Monitor convert to json failed")
            return str(self.to_dict())

    ocr: VideoFrameBuffer
    broadcaster: str
    matcher: ScreenReader
    serialize_rules = ()
    serialize_only = ('id', 'activated_by', 'broadcaster', 'make_clips'
                      , 'min_healing_duration', 'min_elims', 'min_blocking_duration'
                      , 'min_defense_duration', 'min_assist_duration', 'stream_prefers_quality'
                      , 'clip_deaths')
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
    ocr: TwitchEater

    def __init__(self, broadcaster: str, web_dict={}):
        cloud_logger()
        self.broadcaster = broadcaster
        self.web_dict = web_dict
        self.ocr = None

    def start(self):
        cloud_logger()
        has_started = hasattr(self, 'ocr')
        if has_started:
            return
        self.ocr = TwitchEater(self.broadcaster)
        self.matcher = OverwatchScreenReader(self.ocr)
        self.producer_thread = threading.Thread(target=self.ocr.buffer_broadcast, args=[self.matcher])
        self.producer_thread.start()

    def dump(self):
        cloud_logger()
        tmp = self.ocr.buffer
        self.ocr.buffer = Queue()
        while not tmp.empty():
            try:
                tmp.get(False)
            finally:
                return

    def stop(self):
        cloud_logger()
        self.ocr.stop()
        self.matcher.stop()

    def wait_for_stop(self, timeout=None):
        cloud_logger()
        self.producer_thread.join(timeout)


def add_stream_to_monitor(broadcaster: str):
    cloud_logger()
    lower = broadcaster.lower().strip()
    monitor2 = get_monitor_by_name(lower)
    if not monitor2:
        monitor2 = Monitor(lower)
        db.session.add(monitor2)
    monitor2.is_active = True
    db.session.commit()
    db.session.flush()

    return monitor2


def get_all_monitors() -> List[Monitor]:
    cloud_logger()
    return list(Monitor.query.filter_by())


def get_inactive_monitors() -> List[Monitor]:
    cloud_logger()
    return list(Monitor.query.filter_by(is_active=False, avoid=False))


def get_all_my_monitors() -> List[Monitor]:
    cloud_logger()
    return list(Monitor.query.filter_by(activated_by=self_id))


def unclaim_monitor(stream_name) -> Monitor:
    monitor = get_monitor_by_name(stream_name)
    if monitor is None:
        return
    monitor.activated_by = ""
    monitor.activated_at = datetime.datetime(1999, 12, 11, 0, 0)
    db.session.commit()
    db.session.flush()


def claim_monitor(stream_name) -> bool:
    cloud_logger()
    current_time = datetime.datetime.now()
    seven_minutes_ago = current_time - datetime.timedelta(hours=0, minutes=7)
    monitor = get_monitor_by_name(stream_name)
    if monitor is None:
        cloud_message("Could not import " + stream_name + " when looking at streamers")
        return
    time_delta = current_time - datetime.datetime(1999, 12, 11, 0, 0)
    if monitor.activated_at is not None:
        time_delta = current_time - monitor.activated_at
    if monitor.activated_at is None or (time_delta.seconds > 60 * 1 or not monitor.is_active):
        query = Monitor.query.filter_by(
            activated_by=monitor.activated_by, broadcaster=stream_name)
        update_values = {
            Monitor.activated_by: self_id,
            Monitor.activated_at: current_time}
        result = query.update(update_values
                              , synchronize_session=False)
        db.session.commit()
        db.session.flush()
        return result == 1


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
    return Monitor.query.filter_by(broadcaster=stream_name).first()


def cancel_stream_to_monitor(stream_name):
    cloud_logger()
    monitor = get_monitor_by_name(stream_name)
    if not monitor:
        return
    monitor.cancel_request = True
    db.session.commit()
    db.session.flush()


def avoid_monitor(stream_name):
    monitor = get_monitor_by_name(stream_name)
    if not monitor:
        return
    monitor.avoid = True
    db.session.commit()
    db.session.flush()


def remove_stream_to_monitor(stream_name):
    monitor = get_monitor_by_name(stream_name)
    if not monitor:
        return
    monitor.is_active = False
    db.session.commit()
    db.session.flush()
