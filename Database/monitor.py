import threading
from queue import Queue
from typing import List

from sqlalchemy_serializer import SerializerMixin

from Ocr.overwatch_screen_reader import OverwatchScreenReader
from Ocr.screen_reader import ScreenReader
from Ocr.twitch_video_frame_buffer import TwitchEater
from Ocr.video_frame_buffer import VideoFrameBuffer

from config.db_config import db


class Monitor(db.Model, SerializerMixin):
    ocr: VideoFrameBuffer
    broadcaster: str
    matcher: ScreenReader
    serialize_rules = ()
    serialize_only = ('id', 'broadcaster', 'make_clips'
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

    def __init__(self, broadcaster: str, web_dict={}):
        print("Monitor Starting: " + broadcaster)
        self.broadcaster = broadcaster
        self.ocr = TwitchEater(broadcaster)
        self.matcher = OverwatchScreenReader(self.ocr)

        self.web_dict = web_dict

    def start(self):
        self.producer_thread = threading.Thread(target=self.ocr.buffer_broadcast, args=[self.matcher])
        self.producer_thread.start()
    def dump(self):
        tmp = self.ocr.buffer
        self.ocr.buffer = Queue()
        while not tmp.empty():
            try:
                tmp.get(False)
            finally:
                return

    def stop(self):
        self.ocr.stop()
        self.matcher.stop()

    def wait_for_stop(self, timeout=None):
        self.producer_thread.join(timeout)


def add_stream_to_monitor(monitor: Monitor):
    try:
        get_monitor_by_id(monitor.id)
        if not monitor:
            db.session.add(monitor)
        monitor.is_active = True
        db.session.commit()
        db.session.flush()
    except:
        return None
    return monitor


def get_all_monitors() -> List[Monitor]:
    return list(Monitor.query.filter_by(is_active=False))


def get_inactive_monitors() -> List[Monitor]:
    return list(Monitor.query.filter_by(is_active=True))


def get_active_monitors() -> List[Monitor]:
    return list(Monitor.query.filter_by())


def get_monitor_by_id(monitor_id: int) -> Monitor:
    return Monitor.query.filter_by(id=monitor_id).first()


def get_monitor_by_name(stream_name: str) -> Monitor:
    return Monitor.query.filter_by(broadcaster=stream_name).first()


def remove_stream_to_monitor(self, stream_name):
    monitor = get_monitor_by_name(stream_name)
    if not monitor:
        return
    monitor.is_active = False
    db.session.commit()
    db.session.flush()
