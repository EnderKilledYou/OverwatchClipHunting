import threading
from random import shuffle
from threading import Thread
from time import sleep

from monitor import Monitor
from twitch_helpers import get_twitch_api


class MonitorManager:
    _farm_twitch_thread: Thread

    def __init__(self):
        self._farm_twitch_thread = None
        self._monitor_lock = threading.Lock()
        self._monitors = {}
        self.avoids = ['leesibb', 'Seyeumi', 'jay3', 'erinfps', 'guru', 'warn']

    def stop_farm_twitch_mode(self):
        self.farm_twitch = False

    def start_farm_twitch_mode(self):
        if self._farm_twitch_thread and self._farm_twitch_thread.is_alive():
            return
        self._farm_twitch_thread = threading.Thread(target=self.farm_twitch_mode)
        self.farm_twitch = True
        self._farm_twitch_thread.start()

    def farm_twitch_mode(self):
        twitch_api = get_twitch_api()
        while self.farm_twitch:
            sleep(60)
            count = 2 - len(self._monitors)
            if count < 1:
                continue
            streams = twitch_api.get_streams(game_id="488552", language=['en'], first=100)
            if not streams or 'data' not in streams:
                continue
            shuffle(streams['data'])

            for i in range(0, count):
                if len(streams['data']) == 0:
                    break
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

            seconds = qsize / 4
            return {
                'name': name,
                'frames_read': reader.items_read,
                'frames_done': reader.items_drained,
                'seconds': seconds,
                'queue_size': qsize
            }
        return {
            'name': name,
            'seconds': 0,
            'queue_size': 0
        }

    def add_stream_to_monitor(self, stream_name):

        self._monitor_lock.acquire(True, -1)
        try:
            if stream_name.lower() in self.avoids:
                print("avoiding " + stream_name)
                return
            if stream_name not in self._monitors:
                self._monitors[stream_name] = Monitor(stream_name)
        finally:
            self._monitor_lock.release()

    def is_stream_monitored(self, stream_name):
        self._monitor_lock.acquire(True, -1)
        try:
            return stream_name in self._monitors
        finally:
            self._monitor_lock.release()

    def remove_stream_to_monitor(self, stream_name):
        self._monitor_lock.acquire(True, -1)
        try:
            if stream_name not in self._monitors:
                return
            self._monitors[stream_name].stop()
            del self._monitors[stream_name]
        finally:
            self._monitor_lock.release()
