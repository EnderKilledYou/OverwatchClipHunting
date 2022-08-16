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
        self.max_monitored = 2
        self.monitor_list = []
        self.farm_twitch = False
        self._farm_twitch_thread.start()

    def stop_farm_twitch_mode(self):
        self.farm_twitch = False

    def start_farm_twitch_mode(self):
        self.farm_twitch = True

    def heart_beat(self):
        twitch_api = get_twitch_api()
        sleeps = 0
        while True:
            if self.farm_twitch and sleeps % 10 == 0:
                self.farm_twitch(twitch_api)
            sleep(10)

    def farm_twitch(self, twitch_api):
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

            seconds = qsize / 4
            return {
                'name': name,
                'frames_read': reader.items_read * reader.sample_every_count,
                'frames_done': reader.items_drained * reader.sample_every_count,
                'seconds': seconds,
                'queue_size': qsize,
                'data': monitor.web_dict
            }
        return {
            'name': name,
            'seconds': 0,
            'queue_size': 0
        }

    def trim_monitored_streams(self):
        twitch_api = get_twitch_api()
        removes = []
        self._monitor_lock.acquire(True, -1)

        try:
            live_streams_list = self.get_monitored_streams(twitch_api)

            for monitor in self._monitors:
                found = False
                for stream in live_streams_list:
                    if monitor.web_dict['user_login'] == stream['user_login']:
                        found = True
                        monitor.web_dict = stream
                if not found:
                    removes.append(monitor.broadcaster)



        finally:
            self._monitor_lock.release()

        self.remove_streams_to_monitor(removes)

    def get_monitored_streams(self, twitch_api):
        live_streams = twitch_api.get_streams(user_login=list(self._monitors))
        if live_streams and 'data' in live_streams:
            return live_streams['data']
        print("live streams didn't return a valid response")
        return []

    def add_stream_to_monitor(self, stream_name):
        twitch_api = get_twitch_api()
        self._monitor_lock.acquire(True, -1)
        try:
            if stream_name.lower() in self.avoids:
                print("avoiding " + stream_name)
                return
            if stream_name not in self._monitors:
                exists = twitch_api.get_streams(user_login=[stream_name])
                if exists and 'data' in exists and len(exists['data']) == 1:
                    self._monitors[stream_name] = Monitor(stream_name, exists['data'][0])
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
        finally:
            self._monitor_lock.release()
