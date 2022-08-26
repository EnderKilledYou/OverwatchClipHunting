import os

import threading
import traceback
from threading import Timer, Thread
from time import sleep
from typing import List

from Database.live_twitch_instance import LiveTwitchInstance
from Database.unclaim_monitor import unclaim_monitor
from Monitors.heart_beat_helpers import claim_one_monitor
from Ocr.twitch_video_frame_buffer import TwitchEater
from cloud_logger import cloud_logger, cloud_error_logger
from threads.monitor_thread_job import MonitorThreadJob
from twitch_helpers.get_monitored_streams import get_monitored_streams
from twitch_helpers.twitch_helpers import get_twitch_api

from Database.monitor import Monitor, update_claim_on_monitor, get_monitor_stats, release_monitors, get_all_my_monitors


class HeartBeat:
    _claim_timer: Timer

    def __json__(self):
        return "Heartbeat"

    _thread_timer: Thread

    def __init__(self, max_active_monitors=os.cpu_count()):
        self._data_lock = threading.Lock()
        self.max_active_monitors = max_active_monitors + 2
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
            unclaim_monitor(monitor.broadcaster)
            self._remove_monitor_from_list(monitor.broadcaster)

    def start(self):
        cloud_logger()
        self._active = True
        self._thread_timer = threading.Thread(target=self._heart_beat_thread, )
        self._thread_timer.start()

    def stop_streamer(self, streamer_name):
        print(f"Releasing {streamer_name}")
        streamer_names = self.get_copy_active_monitors()
        for active_stream in streamer_names:
            if active_stream.broadcaster == streamer_name:
                self._remove_monitor_from_list(active_stream.broadcaster)
                active_stream.stop()
                del active_stream
                break

    def unclaim_streamer(self, streamer_name):
        unclaim_monitor(streamer_name)

    def reassert_claim(self, monitors: List[Monitor]):
        cloud_logger()
        for monitor in monitors:
            stats = get_monitor_stats(monitor)

            if update_claim_on_monitor(monitor.broadcaster, stats):
                continue

            self.stop_streamer(monitor.broadcaster)

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

    def _start_monitor(self, monitor):
        cloud_logger()
        producer_thread = threading.Thread(target=self.do_broadcast, args=[monitor])
        producer_thread.start()

    def _add_to_monitor_list(self, monitor: Monitor):

        self._data_lock.acquire()
        try:
            thread_job = MonitorThreadJob(monitor.broadcaster)
            thread_job.set_id(monitor.id)
            thread_job.start()
            self._active_monitors.append(thread_job)
        finally:
            self._data_lock.release()

    def _remove_monitor_from_list(self, streamer_name: str):
        self._data_lock.acquire()
        try:
            i = 0
            print(f"finding monitor stopping {streamer_name}")
            for monitor in self._active_monitors:
                if monitor.broadcaster != streamer_name:
                    i = i + 1
                    continue
                print(f"found monitor stopping {streamer_name}")
                self._active_monitors.pop(i)




        except BaseException as e:
            cloud_error_logger(e)
        finally:
            self._data_lock.release()

    def get_copy_active_monitors(self) -> List[MonitorThreadJob]:
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

        monitors = self.get_copy_active_monitors()
        active_monitors = list(map(lambda x: x.broadcaster, monitors))
        already_claimed = list(map(lambda x: x.broadcaster, get_all_my_monitors()))

        not_monitored = list(filter(lambda stream: stream.user_login not in active_monitors, streams))
        not_monitored2 = list(filter(lambda stream: stream.user_login not in already_claimed, not_monitored))

        active_count = len(monitors)
        if active_count < self.max_active_monitors:
            claim = claim_one_monitor(not_monitored2, self.size())
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
                if monitor.broadcaster != stream.user_login:
                    continue
                found = True
                if stream.game_name.lower().startswith("overwatch"):
                    continue
                self.stop_streamer(stream.user_login)  # they changed game
            if not found:
                self.stop_streamer(monitor.broadcaster)  # they stopped stream
