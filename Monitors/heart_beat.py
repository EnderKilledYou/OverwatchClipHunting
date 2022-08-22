import os
import threading
import traceback
from threading import Timer, Thread
from time import sleep
from typing import List

from Database.live_twitch_instance import LiveTwitchInstance
from Database.unclaim_monitor import unclaim_monitor
from Monitors.heart_beat_helpers import claim_one_monitor
from cloud_logger import cloud_logger, cloud_error_logger
from twitch_helpers.get_monitored_streams import get_monitored_streams
from twitch_helpers.twitch_helpers import get_twitch_api

from Database.monitor import Monitor, update_claim_on_monitor, get_monitor_stats, release_monitors


class HeartBeat:
    _claim_timer: Timer

    def __json__(self):
        return "Heartbeat"

    _thread_timer: Thread

    def __init__(self, max_active_monitors=os.cpu_count()):
        self._data_lock = threading.Lock()
        self.max_active_monitors = max_active_monitors
        self._thread_timer = None
        self._claim_timer = None
        self._active = False
        self._active_monitors = []

        self._active_monitor_count = 0

    def update_monitor_healths(self):
        return
        monitors = self.get_copy_active_monitors()
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

    def stop_streamer(self, streamer_name):
        streamer_names = self.get_copy_active_monitors()
        for active_stream in streamer_names:
            if active_stream.broadcaster == streamer_name:
                self._remove_monitor_from_list(active_stream.broadcaster)
                unclaim_monitor(streamer_name)
                break

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
        active_monitors = self.get_copy_active_monitors()
        for monitor in active_monitors:
            unclaim_monitor(monitor.broadcaster)

    def _heart_beat_thread(self):
        cloud_logger()
        twitch_api = get_twitch_api()
        while self._one(twitch_api):
            pass

    def _one(self, twitch_api):
        if not self._active:
            return False
        try:
            self._heart_beat(twitch_api)
            self.reassert_claim(monitors=self.get_copy_active_monitors())
        except BaseException as b:
            cloud_error_logger(b)
            traceback.print_exc()
        sleep(10)
        return True

    def _add_to_monitor_list(self, monitor: Monitor):
        monitor.start()
        self._data_lock.acquire()
        try:
            self._active_monitors.append(monitor)
        finally:
            self._data_lock.release()

    def _remove_monitor_from_list(self, streamer_name: str):
        self._data_lock.acquire()
        try:
            item_range_count = reversed(range(0, len(self._active_monitors)))
            for i in item_range_count:
                monitor = self._active_monitors[i]
                if monitor.Broadcaster == streamer_name:
                    monitor.stop()
                    del self._active_monitors[i]

                    break
        finally:
            self._data_lock.release()

    def delete_monitor_index(self, index) -> List[Monitor]:
        self._data_lock.acquire(True)
        try:
            del self._active_monitors[index]
        finally:
            self._data_lock.release()
            pass

    def get_copy_active_monitors(self) -> List[Monitor]:
        self._data_lock.acquire(True)
        try:
            return list(self._active_monitors)
        finally:
            self._data_lock.release()
            pass

    def _heart_beat(self, twitch_api):
        cloud_logger()
        release_monitors()

        streams: List[LiveTwitchInstance] = get_monitored_streams(twitch_api)
        self._prod_monitors(streams)

        active_monitors = list(map(lambda x: x.Broadcaster, self.get_copy_active_monitors()))

        not_monitored = list(filter(lambda stream: stream.user_login in active_monitors, streams))
        claim = claim_one_monitor(not_monitored, self.size())
        if claim is not None:
            monitor, game = claim
            self._add_to_monitor_list(monitor)
        self.update_monitor_healths()

    def size(self):
        self._data_lock.acquire(True)
        try:
            return len(self._active_monitors)
        finally:
            self._data_lock.release()
            pass

    def _prod_monitors(self, streams):
        monitors = self.get_copy_active_monitors()
        for monitor in monitors:
            found = False
            for stream in streams:
                if monitor.Broadcaster != stream.user_login:
                    continue
                found = True
                if stream.game_name.lower().startswith("overwatch"):
                    continue
                self.stop_streamer(stream.user_login)  # they changed game
            if not found:
                self.stop_streamer(stream.user_login)  # they stopped stream
