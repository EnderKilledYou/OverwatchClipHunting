import threading

from config.streamer_configs import get_streamer_config
from monitor import Monitor


class MonitorManager:
    def __init__(self):
        self._monitor_lock = threading.Lock()
        self._monitors = []

    def get_monitors(self):
        self._monitor_lock.acquire(True, -1)
        try:
            return self._monitors.copy()
        finally:
            self._monitor_lock.release()

    def get_stream_monitors_for_web(self):
        return list(map(self.map_for_web, self.get_monitors()))

    def map_for_web(self, monitor: Monitor):
        qsize = monitor.ocr.buffer.qsize()
        name = monitor.broadcaster
        seconds = qsize / get_streamer_config(name).max_frames_to_scan_per_second
        return {
            'name': name,
            'seconds': seconds,
            'queue_size': qsize
        }

    def add_stream_to_monitor(self, stream_name):
        self._monitor_lock.acquire(True, -1)
        try:
            self._monitors.append(Monitor(stream_name))
        finally:
            self._monitor_lock.release()

    def is_stream_monitored(self, stream_name):
        for monitor in self.get_monitors():
            if monitor.broadcaster == stream_name:
                return True
        return False

    def remove_stream_to_monitor(self, stream_name):
        tmp = []
        for monitor in self.get_monitors():
            if monitor.broadcaster == stream_name:
                monitor.stop()
            else:
                tmp.append(monitor.ocr)
        self.copy_tmp_to_monitors(tmp)

    def copy_tmp_to_monitors(self, tmp):
        self._monitor_lock.acquire(True, -1)
        try:
            self._monitors.clear()
            for i in tmp:
                self._monitors.append(i)
        finally:
            self._monitor_lock.release()
