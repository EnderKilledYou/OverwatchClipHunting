import sys
import threading
import traceback
from random import shuffle
from threading import Thread
from time import sleep
from typing import List

from Database.monitor import Monitor, remove_stream_to_monitor, add_stream_to_monitor, get_monitor_by_name, \
    get_active_monitors, get_all_monitors
from twitch_helpers import get_twitch_api


class MonitorManager:
    _farm_twitch_thread: Thread

    def __init__(self):
        self._farm_twitch_thread = None
        self._monitor_lock = threading.Lock()
        self._monitors = {}
        self.avoids = ['leesibb', 'Seyeumi', 'jay3', 'erinfps', 'guru', 'warn']
        self.max_monitored = 2
        self.monitor_list = []
        self._active = False
        self._farm_twitch_mode = False
        self.max_active_monitors = 3
        self.currently_active_monitors = 0

    def set_farm_twitch_mode(self, mode: bool):
        self._farm_twitch_mode = mode

    def stop_monitor(self):
        self._active = False
        self._farm_twitch_thread.stop()

    def start_monitor(self):
        self._active = False
        while self._farm_twitch_thread and self._farm_twitch_thread.is_alive():
            sleep(10)
        self._farm_twitch_thread = threading.Thread(target=self._heart_beat_thread)
        self._active = True
        self._farm_twitch_thread.start()

    def _heart_beat_thread(self):
        twitch_api = get_twitch_api()
        sleeps = 0
        while self._active:

            if sleeps % 6 == 0:
                self._heart_beat(twitch_api)
            sleep(10)
            sleeps = sleeps + 1

    def _heart_beat(self, twitch_api):
        try:
            self.trim_monitored_streams(twitch_api)
        finally:
            pass
        try:
            if self._farm_twitch_mode:
                self._farm_twitch(twitch_api)
        finally:
            pass

    def _farm_twitch(self, twitch_api):
        count = 2 - len(self._monitors)
        if count < 1:
            return
        streams = twitch_api.get_streams(game_id="488552", language=['en'], first=100)
        if not streams or 'data' not in streams or len(streams['data']) == 0:
            return
        shuffle(streams['data'])
        for i in range(0, count):
            stream = streams['data'].pop()
            self.add_stream_to_monitor(stream['user_login'])

    def avoid_streamer(self, streamer: str):
        self._monitor_lock.acquire(True)
        try:
            if len(streamer) > 0 and streamer.lower() not in self.avoids:
                self.avoids.append(streamer.lower())

        finally:
            self._monitor_lock.release()

        self.remove_stream_to_monitor(streamer)

    def get_monitors(self):
        self._monitor_lock.acquire(True)
        try:
            return list(self._monitors.values())
        finally:
            self._monitor_lock.release()

    def get_stream_monitors_for_web(self):
        return list(map(self.map_for_web, self.get_monitors()))

    def map_for_web(self, monitor: Monitor):
        name = monitor.broadcaster
        reader = monitor.ocr.reader
        if reader:
            qsize = reader.items_read - reader.items_drained

            frames_pending = qsize * reader.sample_every_count
            frames_finished = reader.items_drained * reader.sample_every_count
            back_fill_seconds = frames_pending // reader.fps

            return {
                'name': name,
                'frames_read': reader.items_read * reader.sample_every_count,
                'frames_done': frames_finished,
                'frames_read_seconds': frames_finished // reader.fps,
                'back_fill_seconds': back_fill_seconds,
                'queue_size': qsize,
                'data': monitor.web_dict
            }
        return {
            'name': name,
            'back_fill_seconds': 0,
            'queue_size': 0
        }

    def trim_monitored_streams(self, twitch_api):
        removes = []

        self._monitor_lock.acquire(True, -1)

        try:
            mons = self.get_active_mons(twitch_api)
            if mons is not None:
                self._monitors = mons
        except BaseException as e:
            print(e, file=sys.stderr)
            traceback.print_exc()
            traceback.print_stack()


        finally:
            self._monitor_lock.release()

        self.remove_streams_to_monitor(removes)

    def get_active_mons(self, twitch_api):
        db_monitors = self.get_monitors_from_db_as_dict()
        live_streams_list = self.get_monitored_streams(twitch_api, list(db_monitors))
        for monitor in list(db_monitors):
            lower = monitor.lower()
            streamer_already_monitored = monitor in self._monitors
            if streamer_already_monitored:
                saved_monitor = self._monitors[monitor]
            stream = next(filter(lambda stream: stream['user_login'] == lower, live_streams_list), None)
            if stream is None:
                if not streamer_already_monitored:
                    pass
                else:
                    self._monitors[monitor].stop()
                    self.currently_active_monitors -= 1
                    remove_stream_to_monitor(monitor)

                del db_monitors[monitor]
                continue

            if self.currently_active_monitors >= self.max_active_monitors:
                del db_monitors[monitor]
                continue

            if not streamer_already_monitored:
                saved_monitor = db_monitors[monitor]
                db_monitors[monitor].start()
                self.currently_active_monitors += 1
            saved_monitor.web_dict = stream
            db_monitors[monitor] = saved_monitor

        return db_monitors

    def get_monitors_from_db_as_dict(self):
        tmp = get_all_monitors()
        mons = {}
        for a in tmp:
            mons[a.broadcaster] = a
            a.web_dict = {}
        return mons

    def get_monitored_streams(self, twitch_api, user_logins: List[str]):
        if len(user_logins) == 0:
            return []
        live_streams = twitch_api.get_streams(user_login=user_logins)
        if live_streams and 'data' in live_streams:
            return live_streams['data']
        print("live streams didn't return a valid response")
        return []

    def add_stream_to_monitor(self, stream_name):

        self._monitor_lock.acquire(True, -1)
        try:
            if stream_name.lower() in self.avoids:
                print("avoiding " + stream_name)
                return

            add_stream_to_monitor(stream_name)

        finally:
            self._monitor_lock.release()

    def is_stream_monitored(self, stream_name):
        self._monitor_lock.acquire(True, -1)
        try:
            return stream_name in self._monitors
        finally:
            self._monitor_lock.release()

    def remove_streams_to_monitor(self, streams_name):
        self._monitor_lock.acquire(True, -1)
        try:
            for stream_name in streams_name:
                if stream_name not in self._monitors:
                    continue
                self._monitors[stream_name].stop()
                del self._monitors[stream_name]
        finally:
            self._monitor_lock.release()

    def remove_stream_to_monitor(self, stream_name):
        self._monitor_lock.acquire(True, -1)
        try:
            if stream_name not in self._monitors:
                return
            self._monitors[stream_name].stop()
            del self._monitors[stream_name]
            remove_stream_to_monitor(stream_name)
        finally:
            self._monitor_lock.release()
