import threading

from pyee import EventEmitter

from Ocr.frames.frame import Frame


class FrameAggregator:
    """
        The Frame Aggregator reads multiple frames and routes them. It also trims duplicates.
    """
    last_elim_frame_second: int = -1
    last_elim_frame: int = -1
    last_hero_room_frame: int = -1
    last_elimed_frame: int = -1
    last_healing_frame: int = -1
    last_healing_frame_s: int = -1
    last_prepare_frame: int = -1

    last_escort_frame: int = -1
    last_slept_frame: int = 1
    healing_streak: int = 0
    elim_streak: int = 0
    defense_streak: int = 0
    last_defense_frame: int = -1
    assist_streak: int = 0
    blocking_streak: int = 0
    last_blocking_frame: int = -1
    last_elim_frame_id: int = 0
    last_orbing_frame: int = -1
    last_death_frame: int = -1
    last_assist_frame: int = -1
    elim_count: int = 0
    elim_duration: int = 0
    time_eliminated_mentioned: int = 0
    in_queue: bool = False

    def __init__(self, ee: EventEmitter):
        """

        :param ee: The event emitter to push events to
        """

        self.last_contested_frame = -1
        self.contested_streak = 0
        self.emitter = ee

    def add_elim_frame(self, frame: Frame, elimination_appears_times: int):
        """

        :param frame: the frame that has tested as a elimination frame
        :param elimination_appears_times: the amount of times the frame tested true (for elims, you can have several)
        :return:
        """
        self.check_if_was_queue(frame)
        if self.too_soon_after_death('elim', frame):
            return
        elim_frame_distance = frame.ts_second - self.last_elim_frame
        if self.last_elim_frame != -1 and elim_frame_distance < 1:
            return
        if elim_frame_distance < 4:
            self.elim_streak += 1
            self.elim_duration += elim_frame_distance
        else:
            self.elim_streak = 1
        print_scanner("Hero {1} elim at {0}   ".format(str(frame.ts_second), frame.source_name))
        self.last_elim_frame = frame.ts_second
        thread_function(self.emitter.emit, 'elim', frame, self.elim_streak, self.elim_duration, self.last_death_frame)

    def too_soon_after_death(self, event_name, frame):
        time_since_last_death = frame.ts_second - self.last_death_frame
        if time_since_last_death < 0:
            time_since_last_death = 1
        if self.last_death_frame != -1 and 9 > time_since_last_death > 0:
            print_scanner(
                "Skipping {3} {2} at {0}, seconds since last death: {1}  ".format(str(frame.ts_second),
                                                                                  time_since_last_death, event_name,
                                                                                  frame.source_name))
            return True
        return False

    def add_elimed_frame(self, frame):
        self.check_if_was_queue(frame)
        elim_frame_distance = frame.ts_second - self.last_death_frame
        if elim_frame_distance < 9:
            return
        self.last_death_frame = frame.ts_second
        thread_function(self.emitter.emit, 'elimed', frame)
        print_scanner("Death {1} at {0} ".format(str(frame.ts_second), frame.source_name))

    def add_spawn_room_frame(self, frame):
        self.check_if_was_queue(frame)
        self.elim_count = 0
        self.elim_duration = 0
        elim_frame_distance = frame.ts_second - self.last_hero_room_frame
        if self.last_hero_room_frame != -1 and elim_frame_distance <= 9:
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
            return
        slept_frame_distance = frame.ts_second - self.last_slept_frame
        if self.last_slept_frame != -1 and slept_frame_distance < 4:
            return

        print_scanner("Hero {1} slepted at {0}   ".format(str(frame.ts_second), frame.source_name))
        thread_function(self.emitter.emit, 'slept', frame)
        self.last_slept_frame = frame.ts_second

    def add_healing_frame(self, frame):
        if self.too_soon_after_death('heal', frame):
            return
        if frame.frame_number < self.last_healing_frame:
            print_scanner(
                "Skipping {3} Heal at {0}, out of order second: {1} Frame num {1} Last Frame {2}  ".format(
                    str(frame.ts_second),
                    frame.frame_number, self.last_healing_frame, frame.source_name))
            return
        heal_frame_distance = frame.frame_number - self.last_healing_frame
        heal_frame_distance_s = frame.ts_second - self.last_healing_frame_s
        if self.last_healing_frame != -1 and heal_frame_distance < 2:
            print_scanner("Hero {1} skipped Healed at {0}  because distance was {2}  ".format(str(frame.ts_second),
                                                                                      frame.source_name,
                                                                                      heal_frame_distance))
            return
        if heal_frame_distance_s < 6:
            self.healing_streak += 1
        else:
            self.healing_streak = 1
        print_scanner("Hero {1} Healed at {0}   ".format(str(frame.ts_second), frame.source_name))
        thread_function(self.emitter.emit, 'healing', frame, self.healing_streak)
        self.last_healing_frame_s = frame.ts_second
        self.last_healing_frame = frame.frame_number

    def add_orb_gained_frame(self, frame):
        if self.too_soon_after_death('orb', frame):
            return
        orb_frame_distance = frame.ts_second - self.last_orbing_frame
        if self.last_orbing_frame != -1 and orb_frame_distance < 2:
            return
        print_scanner("Hero {1} orbed at {0}   ".format(str(frame.ts_second), frame.source_name))
        thread_function(self.emitter.emit, 'orbed', frame)
        self.last_orbing_frame = frame.ts_second

    def add_blocking_frame(self, frame):
        if self.too_soon_after_death('blocking', frame):
            return
        blocking_frame_distance = frame.ts_second - self.last_blocking_frame
        if self.last_blocking_frame != -1 and blocking_frame_distance < 1:
            return
        if blocking_frame_distance < 4:
            self.blocking_streak += 1
        else:
            self.blocking_streak = 1
        print_scanner("Hero {1} blocking at {0}   ".format(str(frame.ts_second), frame.source_name))
        thread_function(self.emitter.emit, 'blocking', frame, self.blocking_streak)
        self.last_blocking_frame = frame.ts_second

    def set_in_queue(self, frame):
        if self.in_queue:
            return
        print_scanner("{1} in queue at {0}   ".format(str(frame.ts_second), frame.source_name))
        thread_function(self.emitter.emit, 'queue_start', frame)
        self.in_queue = True

    def set_in_prepare(self, frame, mode):
        self.check_if_was_queue(frame)
        if self.last_prepare_frame != -1:
            prepare_frame_distance = frame.ts_second - self.last_prepare_frame
            if prepare_frame_distance < 10:
                return
        print_scanner("Hero {1} Prepared at {0}   ".format(str(frame.ts_second), frame.source_name))
        thread_function(self.emitter.emit, 'prepare', frame, mode)
        self.last_prepare_frame = frame.ts_second

    def add_assist_frame(self, frame):
        self.check_if_was_queue(frame)
        if self.too_soon_after_death('assist', frame):
            return
        assist_frame_distance = frame.ts_second - self.last_assist_frame
        if self.last_assist_frame != -1 and assist_frame_distance < 1:
            return
        if assist_frame_distance < 4:
            self.assist_streak += 1
        else:
            self.assist_streak = 1
        print_scanner("Hero {1} assist at {0}   ".format(str(frame.ts_second), frame.source_name))
        thread_function(self.emitter.emit, 'assist', frame, self.assist_streak)
        self.last_assist_frame = frame.ts_second

    def add_escort_frame(self, frame):
        self.check_if_was_queue(frame)
        print_scanner("Hero {1} escort at {0}   ".format(str(frame.ts_second), frame.source_name))
        self.last_escort_frame = frame.ts_second

    def add_contested_frame(self, frame):
        self.check_if_was_queue(frame)

        if self.too_soon_after_death('contested', frame):
            return
        contested_frame_distance = frame.ts_second - self.last_contested_frame
        if self.last_contested_frame != -1 and contested_frame_distance < 1:
            return
        if contested_frame_distance < 6:
            self.contested_streak += 1
        else:
            self.contested_streak = 1
        print_scanner("Hero {1} contested at {0}   ".format(str(frame.ts_second), frame.source_name))
        thread_function(self.emitter.emit, 'contested', frame, self.contested_streak)
        self.last_contested_frame = frame.ts_second

    def add_defense_frame(self, frame):
        self.check_if_was_queue(frame)
        if self.too_soon_after_death('defense', frame):
            return
        defense_frame_distance = frame.ts_second - self.last_defense_frame
        if self.last_defense_frame != -1 and defense_frame_distance < 1:
            return
        if defense_frame_distance < 6:
            self.defense_streak += 1
        else:
            self.defense_streak = 1
        print_scanner("Hero {1} defense at {0}   ".format(str(frame.ts_second), frame.source_name))
        thread_function(self.emitter.emit, 'defense', frame, self.defense_streak)
        self.last_defense_frame = frame.ts_second


def thread_function(func, *args):  # the events can slow down processing
    t = threading.Thread(target=func, args=args)
    t.start()
    return t


def print_scanner(data):
    print(f'|CLOUD FRAME LOG: {data}|')