import threading
from threading import Thread

from Database.monitor import add_stream_to_monitor, get_all_monitors, avoid_monitor
from cloud_logger import cloud_logger, cloud_error_logger, cloud_message



class MonitorManager():
    _farm_twitch_thread: Thread

    def __repr__(self):
        return "(Monitor Manager)"

    def __json__(self):
        return 'Monitor Manager'

    def __str__(self):
        return "Monitor Manager"

    def update_web_dicts(self, streams):
        for st in streams:
            if st['user_login'] in self._monitors:
                self._monitors[st['user_login']].web_dict = st

    def __init__(self):
        self.live_stream = []
        self._farm_twitch_thread = None
        self._monitor_lock = threading.Lock()
        self._monitors = {}
        self._active = False

        self._farm_twitch_mode = False
        self.max_twitch_farms = 4
        self.max_active_monitors = 10
        self.currently_active_monitors = 0



    def stop_monitor(self):
        cloud_logger()
        self.heart.stop()
        self._active = False
        self._farm_twitch_thread.stop()

    def start_manager(self):
        cloud_logger()
        self._active = False
        self.heart.start()
        self._active = True




    def avoid_streamer(self, streamer: str):
        cloud_logger()
        avoid_monitor(streamer)
        self.remove_stream_to_monitor(streamer)

    def get_monitors(self):
        self._monitor_lock.acquire()
        try:
            return list(self._monitors.values())
        finally:
            self._monitor_lock.release()

    def get_stream_monitors_for_web(self):

        monitors = get_all_monitors()
        if len(monitors) == 0:
            return []
        streams = self.live_stream
        found = []
        for a in monitors:
            c = None
            for b in streams:
                if a.broadcaster == b['user_login']:
                    c = b
                    break
            found.append((a, c))

        return list(map(lambda a: self.map_for_web(a[0], a[1]), found))



    def map_for_web(self, monitor, data):

        name = monitor.broadcaster
        if name in self._monitors:
            monitor = self._monitors[name]
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
                    'fps': reader.fps,
                    'queue_size': qsize,
                    'stream_resolution': monitor.ocr.stream_res,
                    'data': data
                }
        return {
            'name': name,
            'frames_read': 0,
            'frames_done': 0,
            'frames_read_seconds': 0,
            'back_fill_seconds': 0,
            'fps': 0,
            'queue_size': '',
            'stream_resolution': '',
            'data': data
        }

    def get_monitors_from_db_as_dict(self):
        cloud_logger()
        tmp = get_all_monitors()
        mons = {}
        for a in tmp:
            mons[a.broadcaster] = a
            a.web_dict = {}
        return mons



    def add_stream_to_monitor(self, stream_name):
        cloud_logger()

        add_stream_to_monitor(stream_name)

    def remove_streams_to_monitor(self, streams_name):
        cloud_logger()

        for stream_name in streams_name:
            if stream_name not in self._monitors:
                continue
            self._monitors[stream_name].stop()
            del self._monitors[stream_name]

    def remove_stream_to_monitor(self, stream_name):
        cloud_logger()
        if stream_name not in self._monitors:
            cloud_message(f"Could not find {stream_name} in self monitor")
            return
        self._monitor_lock.acquire()
        try:
            monitor = self._monitors[stream_name]
            del self._monitors[stream_name]
        except BaseException as b:
            cloud_error_logger(b)
        finally:
            self._monitor_lock.release()
        if monitor is not None:
            monitor.stop()
