import sys
import threading
import traceback
from random import shuffle
from threading import Thread
from time import sleep
from typing import List

from Database.monitor import Monitor, remove_stream_to_monitor, add_stream_to_monitor, get_monitor_by_name, \
    get_active_monitors, get_all_monitors, avoid_monitor, claim_monitor, get_all_my_monitors, unclaim_monitor, \
    get_active_monitors_names, self_id, get_my_active_monitors
from cloud_logger import cloud_logger, cloud_error_logger, cloud_message
from twitch_helpers import get_twitch_api


class MonitorManager():
    _farm_twitch_thread: Thread

    def __repr__(self):
        return "(Monitor Manager)"

    def __json__(self):
        return 'Monitor Manager'

    def __str__(self):
        return "Monitor Manager"

    def __init__(self):
        self._farm_twitch_thread = None
        self._monitor_lock = threading.Lock()
        self._monitors = {}
        self._active = False

        self._farm_twitch_mode = False
        self.max_twitch_farms = 4
        self.max_active_monitors = 10
        self.currently_active_monitors = 0

    def set_farm_twitch_mode(self, mode: bool):
        cloud_logger()
        self._farm_twitch_mode = mode

    def stop_monitor(self):
        cloud_logger()
        self._active = False
        self._farm_twitch_thread.stop()

    def start_manager(self):
        cloud_logger()
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
            self._heart_beat(twitch_api)
            sleep(10)

    def unclaim_dead_streams(self, monitors, live_streams_list):

        stopped = filter(lambda x: x in self._monitors and not self._monitors[x].ocr._active, monitors)
        for streamer_name in stopped:
            del self._monitors[streamer_name]
            remove_stream_to_monitor(streamer_name)
            self.currently_active_monitors -= 1
            unclaim_monitor(streamer_name)

        currently_monitored = map(lambda x: x['user_login'],
                                  filter(lambda x: x['user_login'] in monitors, live_streams_list))
        expired = list(filter(lambda x: x not in currently_monitored, self._monitors))

        for streamer_name in expired:
            self._monitors[streamer_name].stop()
            del self._monitors[streamer_name]
            remove_stream_to_monitor(streamer_name)
            self.currently_active_monitors -= 1
            unclaim_monitor(streamer_name)

    def _heart_beat(self, twitch_api):
        cloud_logger()
        try:
            monitors, streams = self.get_state(twitch_api)

        except BaseException as b:

            cloud_error_logger(b)
            return
        self._monitor_lock.acquire()
        try:
            self.unclaim_dead_streams(monitors, streams)
            self.claim_one_monitor(monitors, streams)
            self.start_unstarted_monitors(streams)
            self.update_web_dicts(streams)
            self.update_monitor_healths()
        except BaseException as b:

            cloud_error_logger(b)
        finally:
            self._monitor_lock.release()

    def update_monitor_healths(self):
        for a in self._monitors:
            self.check_need_restart(self._monitors[a])

    def update_web_dicts(self, streams):
        for st in streams:
            if st['user_login'] in self._monitors:
                self._monitors[st['user_login']].web_dict = st

    def get_state(self, twitch_api):
        monitors = self.get_monitors_from_db_as_dict()

        streams = self.get_monitored_streams(twitch_api, list(monitors))
        return monitors, streams

    def _farm_twitch(self, twitch_api):
        cloud_logger()
        count = self.max_twitch_farms - len(self._monitors)
        if count < 1:
            return
        streams = twitch_api.get_streams(game_id="488552", language=['en'], first=100)
        if not streams or 'data' not in streams or len(streams['data']) == 0:
            return
        shuffle(streams['data'])
        for i in range(0, count):
            stream = streams['data'].pop()
            self.add_stream_to_monitor(stream['user_login'])

    def claim_one_monitor(self, twitch_api, streams):
        cloud_logger()
        if self.currently_active_monitors >= self.max_active_monitors:
            cloud_message("No space to start new streamers")
            return

        for stream in streams:
            claimed = claim_monitor(stream['user_login'])
            if claimed:
                self.currently_active_monitors += 1
                return

    def start_unstarted_monitors(self, live_streams_list):
        monitors = get_all_my_monitors()
        monitors_dict = {}
        for monitor in monitors:
            monitors_dict[monitor.broadcaster] = monitor

        db_monitors = list(filter(lambda x: x.activated_by == self_id, monitors))
        currently_monitored = list(self._monitors)
        unstarted = list(filter(lambda x: x not in currently_monitored, db_monitors))
        unstarted_names = list(map(lambda x: x.broadcaster, unstarted))
        live_streamers = filter(lambda x: x['user_login'] in unstarted_names, live_streams_list)
        for streamer in live_streamers:
            user_login = streamer['user_login']
            self._monitors[user_login] = monitors_dict[user_login]
            monitors_dict[user_login].start()

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
        twitch_api = get_twitch_api()
        streams = self.get_monitored_streams(twitch_api, list(map(lambda x: x.broadcaster, monitors)))
        found = []
        for a in monitors:
            c = None
            for b in streams:
                if a.broadcaster == b['user_login']:
                    c = b
                    break
            found.append((a, c))

        return  list(map(lambda a:self.map_for_web(a[0],a[1]), found))

    def check_need_restart(self, monitor: Monitor):
        reader = monitor.ocr.reader
        if not reader:
            return
        qsize = reader.items_read - reader.items_drained
        frames_pending = qsize * reader.sample_every_count
        back_fill_seconds = frames_pending // reader.fps
        if back_fill_seconds <= 180:
            return
        cloud_message("Restarting " + monitor.broadcaster + " with backqueue of " + back_fill_seconds)
        monitor.stop()
        remove_stream_to_monitor(monitor.broadcaster)

    def map_for_web(self, monitor,data):

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

    def trim_monitored_streams(self, twitch_api):
        cloud_logger()

        mons = self.calc_monitor_list(twitch_api)
        if mons is not None:
            self.swap_in_new_monitor(mons)

    def calc_monitor_list(self, twitch_api):
        try:
            mons = self.get_active_mons(twitch_api)
        except BaseException as e:
            cloud_error_logger(e, file=sys.stderr)
            traceback.print_exc()
            traceback.print_stack()
            return None
        return mons

    def swap_in_new_monitor(self, mons):
        self._monitor_lock.acquire()
        try:
            self._monitors = mons
        except BaseException as e:
            cloud_error_logger(e, file=sys.stderr)
            traceback.print_exc()
            traceback.print_stack()
        finally:
            self._monitor_lock.release()

    # def get_active_mons(self, twitch_api):
    #     cloud_logger()
    #     db_monitors = self.get_monitors_from_db_as_dict()
    #     live_streams_list = self.get_monitored_streams(twitch_api, list(db_monitors))
    #     for streamer_name in list(db_monitors):
    #
    #         streamer_already_monitored = streamer_name in self._monitors
    #         stream = self.get_stream_from_live_list(live_streams_list, streamer_name)
    #         if streamer_already_monitored:
    #             db_monitors[streamer_name] = self._monitors[streamer_name]
    #             if stream is None:
    #                 self._monitors[streamer_name].stop()
    #                 self.currently_active_monitors -= 1
    #                 del db_monitors[streamer_name]
    #                 remove_stream_to_monitor(streamer_name)
    #                 continue
    #
    #             continue
    #         if not stream or self.currently_active_monitors >= self.max_active_monitors:
    #             del db_monitors[streamer_name]
    #             continue
    #
    #         db_monitors[streamer_name].start()
    #         self.currently_active_monitors += 1
    #
    #     return db_monitors

    # def get_stream_from_live_list(self, live_streams_list, streamer_name):
    #     lower = streamer_name.lower()
    #     stream = next(filter(lambda live_stream: live_stream['user_login'] == lower, live_streams_list), None)
    #     return stream

    def get_monitors_from_db_as_dict(self):
        cloud_logger()
        tmp = get_all_monitors()
        mons = {}
        for a in tmp:
            mons[a.broadcaster] = a
            a.web_dict = {}
        return mons

    def get_monitored_streams(self, twitch_api, user_logins: List[str]):
        cloud_logger()
        if len(user_logins) == 0:
            return []
        live_streams = twitch_api.get_streams(user_login=user_logins)
        if live_streams and 'data' in live_streams:
            return live_streams['data']
        print("live streams didn't return a valid response")
        return []

    def add_stream_to_monitor(self, stream_name):
        cloud_logger()

        add_stream_to_monitor(stream_name)

    # def is_stream_monitored(self, stream_name):
    #     cloud_logger()
    #     self._monitor_lock.acquire(True, -1)
    #     try:
    #         return stream_name in self._monitors
    #     finally:
    #         self._monitor_lock.release()

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
            return
        self._monitors[stream_name].stop()
