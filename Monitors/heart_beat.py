import threading
import traceback
from threading import Timer, Thread
from time import sleep
from typing import List

from Database.monitor import unclaim_monitor, Monitor, update_claim_on_monitor, get_monitor_stats, release_monitors, \
    get_all_monitors
from Monitors.heart_beat_helpers import claim_one_monitor
from cloud_logger import cloud_logger, cloud_error_logger
from twitch_helpers.get_monitored_streams import get_monitored_streams
from twitch_helpers.twitch_helpers import get_twitch_api


class HeartBeat:
    _claim_timer: Timer

    def __json__(self):
        return "Heartbeat"

    monitor: Monitor
    _thread_timer: Thread

    def __init__(self, max_active_monitors=5):

        self.max_active_monitors = max_active_monitors
        self._thread_timer = None
        self._claim_timer = None
        self._active = False
        self._active_monitors = []

        self._active_monitor_count = 0

    def update_monitor_healths(self, monitors: List[Monitor]):
        for monitor in monitors:

            needs = monitor.check_need_restart()
            if not needs:
                continue
            unclaim_monitor(monitor.Broadcaster)
            self._remove_monitor_from_list(monitor.Broadcaster)

    def start(self):
        cloud_logger()
        self._active = True
        self._thread_timer = threading.Thread(target=self._heart_beat_thread, )
        self._thread_timer.start()

    def reassert_claim(self, monitors: List[Monitor]):
        cloud_logger()
        for monitor in monitors:
            stats = get_monitor_stats(monitor)
            if update_claim_on_monitor(monitor.Broadcaster, stats):
                continue
            self._remove_monitor_from_list(monitor.broadcaster)

    def stop(self):
        cloud_logger()
        self._active = False
        self._thread_timer.cancel()

    def _heart_beat_thread(self):
        cloud_logger()
        twitch_api = get_twitch_api()
        while True:
            try:
                self._heart_beat(twitch_api)
                self.reassert_claim(monitors=self.get_copy_active_monitors())
            except BaseException as b:
                cloud_error_logger(b)
                traceback.print_exc()
            sleep(20)

    def _add_to_monitor_list(self, monitor: Monitor):
        monitor.start()
        self._active_monitors.append(monitor)

    def _remove_monitor_from_list(self, streamer_name: str):
        item_range_count = reversed(range(0, len(self.get_copy_active_monitors())))
        for i in item_range_count:
            monitor = self._active_monitors[i]
            if monitor.Broadcaster == streamer_name:
                monitor.stop()
                del self._active_monitors[i]

                break

    def get_copy_active_monitors(self) -> List[Monitor]:
        return list(self._active_monitors)

    def _heart_beat(self, twitch_api):
        cloud_logger()
        release_monitors()

        streams = get_monitored_streams(twitch_api)

        monitor = claim_one_monitor(streams, len(self._active_monitors))
        if monitor is not None:
            self._add_to_monitor_list(monitor)
        # self.update_monitor_healths(monitors)
