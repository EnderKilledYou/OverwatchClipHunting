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
        name = monitor.broadcaster
        reader = monitor.ocr.reader
        if reader:
            qsize = reader.items_read - reader.items_drained

            seconds = qsize / 4
            return {
                'name': name,
                'frames_read':reader.items_read,
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
                tmp.append(monitor)
        self.copy_tmp_to_monitors(tmp)

    def copy_tmp_to_monitors(self, tmp):
        self._monitor_lock.acquire(True, -1)
        try:
            self._monitors.clear()
            for i in tmp:
                self._monitors.append(i)
        finally:
            self._monitor_lock.release()
