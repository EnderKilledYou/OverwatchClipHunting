import threading

from pyee import EventEmitter

from Ocr.frames.frame import Frame


class FrameCompactor:

    def add(self, other: Frame):
        if self.last_frame == -1:
            self.reset_streak(other)
            return False
        if self.last_frame > other.frame_number:
            print(f"Skipping frame out of order {other.frame_number}")
            return True
        second_distance = other.ts_second - self.last_second
        if second_distance == 0:
            return True
        if second_distance > self._second_distance:
            self.reset_streak(other)
            return False
        self.streak_size = self.streak_size + 1
        self.last_second = other.ts_second
        self.streak_size_seconds = other.ts_second - self.streak_start_second
        return False

    def reset_streak(self, other):
        self.last_frame = other.frame_number
        self.last_second = other.ts_second
        self.streak_start_second = other.ts_second
        self.streak_size = 1
        self.streak_size_seconds = 0

    def __init__(self, second_distance: int):

        self._second_distance = second_distance
        self.last_frame = -1
        self.last_second = -1
        self.streak_start_second = -1
        self.streak_size = -1
        self.streak_size_seconds = -1


class FrameAggregator:
    """
        The Frame Aggregator reads multiple frames and routes them. It also trims duplicates.
    """

    def __del__(self):
        print(f"{__qualname__} Del")
        if hasattr(self, 'emitter'):
            del self.emitter
            del self.healing_frame_watcher
            del self.orb_frame_watcher
            del self.elim_frame_watcher
            del self.elimed_frame_watcher
            del self.defense_frame_watcher
            del self.assist_frame_watcher
            del self.blocking_frame_watcher
            del self.slept_frame_watcher

    def __init__(self, ee: EventEmitter):
        """

        :param ee: The event emitter to push events to
        """
        self.healing_frame_watcher = FrameCompactor(5)
        self.orb_frame_watcher = FrameCompactor(5)
        self.elim_frame_watcher = FrameCompactor(5)
        self.elimed_frame_watcher = FrameCompactor(5)
        self.prepare_frame_watcher = FrameCompactor(5)
        self.defense_frame_watcher = FrameCompactor(5)
        self.assist_frame_watcher = FrameCompactor(5)
        self.contested_frame_watcher = FrameCompactor(5)
        self.blocking_frame_watcher = FrameCompactor(5)
        self.slept_frame_watcher = FrameCompactor(5)
        self.last_hero_room_frame = -1
        self.in_queue = False

        self.emitter = ee

    def add_elim_frame(self, frame: Frame, elimination_appears_times: int):
        """

        :param frame: the frame that has tested as a elimination frame
        :param elimination_appears_times: the amount of times the frame tested true (for elims, you can have several)
        :return:
        """
        if self.too_soon_after_death('elim', frame):
            del frame
            return

        if self.elim_frame_watcher.add(frame):
            del frame
            return

        print_scanner("Hero {1} made elim at {0}   ".format(str(frame.ts_second), frame.source_name))

        thread_function(self.emitter.emit, 'elim', frame,
                        self.elim_frame_watcher.streak_size, self.elim_frame_watcher.streak_size_seconds,
                        self.elimed_frame_watcher.last_second)

    def too_soon_after_death(self, event_name, frame):

        if self.elimed_frame_watcher.last_second == -1:
            return False
        time_since_last_death = frame.ts_second - self.elimed_frame_watcher.last_second
        if time_since_last_death < 0:
            time_since_last_death = 1
        if self.elimed_frame_watcher.last_frame != -1 and 9 > time_since_last_death > 0:
            print_scanner(
                "Skipping {3} {2} at {0}, seconds since last death: {1}  ".format(str(frame.ts_second),
                                                                                  time_since_last_death, event_name,
                                                                                  frame.source_name))
            return True
        return False

    def add_elimed_frame(self, frame):
        self.check_if_was_queue(frame)
        if self.elimed_frame_watcher.add(frame):
            del frame
            return
        thread_function(self.emitter.emit, 'elimed', frame)
        print_scanner("Death {1} at {0} ".format(str(frame.ts_second), frame.source_name))

    def add_spawn_room_frame(self, frame):
        self.check_if_was_queue(frame)

        elim_frame_distance = frame.ts_second - self.last_hero_room_frame
        if self.last_hero_room_frame != -1 and elim_frame_distance <= 9:
            del frame
            return
        print_scanner("Hero {1} Select at {0}   ".format(str(frame.ts_second), frame.source_name))
        thread_function(self.emitter.emit, 'spawn_room', frame)
        self.last_hero_room_frame = frame.ts_second

    def check_if_was_queue(self, frame):
        if self.in_queue:
            thread_function(self.emitter.emit, 'game_start', frame)
            self.in_queue = False

    def add_slepting_frame(self, frame):
        if self.too_soon_after_death('slept', frame):
            del frame
            return
        if self.slept_frame_watcher.add(frame):
            del frame
            return

        print_scanner("Hero {1} slepted at {0}   ".format(str(frame.ts_second), frame.source_name))

        thread_function(self.emitter.emit, 'slept', frame)

    def add_healing_frame(self, frame):
        if self.too_soon_after_death('heal', frame):
            del frame
            return
        if self.healing_frame_watcher.add(frame):
            del frame
            return

        print_scanner("Hero {1} Healed at {0}   ".format(str(frame.ts_second), frame.source_name))

        thread_function(self.emitter.emit, 'healing', frame, (
            self.healing_frame_watcher.streak_start_second, self.healing_frame_watcher.streak_size,
            self.healing_frame_watcher.streak_size_seconds))

    def add_orb_gained_frame(self, frame):
        if self.too_soon_after_death('orb', frame):
            del frame
            return
        if self.orb_frame_watcher.add(frame):
            del frame
            return
        thread_function(self.emitter.emit, 'orbed', frame)

    def add_blocking_frame(self, frame):
        if self.too_soon_after_death('blocking', frame):
            del frame
            return
        if self.blocking_frame_watcher.add(frame):
            del frame
            return
        thread_function(self.emitter.emit, 'blocking', frame, self.blocking_frame_watcher.streak_size_seconds)

    def set_in_queue(self, frame):
        if self.in_queue:
            del frame
            return
        print_scanner("{1} in queue at {0}   ".format(str(frame.ts_second), frame.source_name))
        thread_function(self.emitter.emit, 'queue_start', frame)
        self.in_queue = True

    def set_in_prepare(self, frame, mode):
        self.check_if_was_queue(frame)
        if self.prepare_frame_watcher.add(frame):
            del frame
            return
        thread_function(self.emitter.emit, 'prepare', frame, mode)

    def add_assist_frame(self, frame):
        self.check_if_was_queue(frame)
        if self.too_soon_after_death('assist', frame):
            del frame
            return
        if self.assist_frame_watcher.add(frame):
            del frame
            return
        thread_function(self.emitter.emit, 'assist', frame, self.assist_frame_watcher.streak_size_seconds)


    def add_escort_frame(self, frame):
        self.check_if_was_queue(frame)
        print_scanner("Hero {1} escort at {0}   ".format(str(frame.ts_second), frame.source_name))
        del frame

    def add_contested_frame(self, frame):
        self.check_if_was_queue(frame)

        if self.too_soon_after_death('contested', frame):
            del frame
            return
        if self.contested_frame_watcher.add(frame):
            del frame
            return
        thread_function(self.emitter.emit, 'contested', frame, self.contested_frame_watcher.streak_size_seconds)

    def add_defense_frame(self, frame):
        self.check_if_was_queue(frame)
        if self.too_soon_after_death('defense', frame):
            del frame
            return
        if self.defense_frame_watcher.add(frame):
            del frame
            return
        thread_function(self.emitter.emit, 'defense', frame, self.defense_frame_watcher.streak_size_seconds)


def thread_function(func, *args):  # the events can slow down processing
    t = threading.Thread(target=func, args=args)
    t.start()
    return t


def print_scanner(data):
    print(f'|CLOUD FRAME LOG: {data}|')
