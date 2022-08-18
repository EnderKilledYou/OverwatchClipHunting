import threading
from threading import Timer
from typing import Dict, List

from Database.monitor import unclaim_monitor, Monitor, update_claim_on_monitor
from claim_monitor import ClaimMonitor
from cloud_logger import cloud_logger
from get_monitored_streams import get_monitored_streams
from monitor_manager import MonitorManager
from twitch_helpers import get_twitch_api


class HeartBeat():
    _claim_timer: Timer

    def __repr__(self):
        return "Alli"

    def __json__(self):
        return 'Alli'

    def __str__(self):
        return "Alli"

    monitor: Monitor
    _thread_timer: Timer

    def __init__(self, max_active_monitors=5):

        self.max_active_monitors = max_active_monitors
        self._thread_timer = None
        self._claim_timer = None
        self._active = False
        self._active_monitors = []
        self.claim_manager = ClaimMonitor()
        self._active_monitor_count = 0

    def update_monitor_healths(self, monitors: Dict[str, Monitor]):
        for monitor_name in monitors:
            monitor = self._monitors[monitor_name]
            needs = monitor.check_need_restart()
            if not needs:
                continue
            unclaim_monitor(monitor_name)
            self._remove_monitor_from_list(monitor_name)

    def start(self):
        cloud_logger()

        self._active = True

        self._beat()
        self._heart_beat_thread()

    def _beat(self):
        cloud_logger()
        if self._active:
            self._thread_timer = threading.Timer(15, self._heart_beat_thread, )
            self._thread_timer.start()

            monitors = self.get_copy_active_monitors()
            self._claim_timer = threading.Timer(interval=1, function=self.reassert_claim, args=[monitors])
            self._claim_timer.start()

    def reassert_claim(self, monitors: List[Monitor]):
        cloud_logger()
        for monitor in monitors:
            if update_claim_on_monitor(monitor.Broadcaster):
                continue
            self._remove_monitor_from_list(monitor.broadcaster)

    def stop(self):
        cloud_logger()
        self._active = False
        self._thread_timer.cancel()

    def _heart_beat_thread(self):
        cloud_logger()
        twitch_api = get_twitch_api()
        self._heart_beat(twitch_api)
        self._beat()

    def _add_to_monitor_list(self, monitor: Monitor):
        monitor.start()
        self._active_monitors.append(monitor)

    def _remove_monitor_from_list(self, streamer_name: str):

        for i in reversed(range(0, len(self._active_monitors))):
            monitor = self._active_monitors[i]
            if monitor.Broadcaster == streamer_name:
                monitor.stop()
                del self._active_monitors[i]

                break

    def get_copy_active_monitors(self) -> List[Monitor]:
        return list(self._active_monitors)

    def _heart_beat(self, twitch_api):
        cloud_logger()
        monitors = self.get_copy_active_monitors()
        streams = get_monitored_streams(twitch_api, monitors)
        monitor = self.claim_manager.claim_one_monitor( streams)
        if monitor is not None:
            self._add_to_monitor_list(monitor)
        self.update_monitor_healths(monitors)


def list_to_dict(monitors: List[Monitor]):
    monitors_dict = {}
    for monitor in monitors:
        monitors_dict[monitor.broadcaster] = monitor
    return monitors_dict


alli = HeartBeat()
