from pyee import EventEmitter

from Ocr.frame import Frame


class FrameAggregator:
    """
        The Frame Aggregator reads multiple frames and routes them. It also trims duplicates.
    """
    last_elim_frame: int = -1
    last_hero_room_frame: int = -1
    last_elimed_frame: int = -1
    last_healing_frame: int = -1
    last_prepare_frame: int = -1
    last_prepare_frame: int = -1
    healing_streak: int = 0
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

    def __init__(self, ee: EventEmitter) -> object:
        """

        :param ee: The event emitter to push events to
        """

        self.emitter = ee

    def add_elim_frame(self, frame: Frame, elimination_appears_times: int):
        """

        :param frame: the frame that has tested as a elimination frame
        :param elimination_appears_times: the amount of times the frame tested true (for elims, you can have several)
        :return:
        """
        self.check_if_was_queue(frame)
        if self.last_elim_frame_id > frame.frame_number:
            print(
                "Skipping {3} Kill at {0}, out of order second: {1} Frame num {1} Last Frame {2}  ".format(
                    str(frame.ts_second),
                    frame.frame_number, self.last_elim_frame_id, frame.source_name))
            return
        self.last_elim_frame_id = frame.frame_number

        if self.too_soon_after_death('elim', frame):
            return

        if self.last_elim_frame == -1:
            time_since_last_kill = 3
            self.last_elim_frame = frame.ts_second
        else:
            elim_frame = self.last_elim_frame
            time_since_last_kill = frame.ts_second - elim_frame
            self.last_elim_frame = frame.ts_second
            if time_since_last_kill < 1:
                print(
                    "Skipping {3} Kill at {0}, time since last kill is too soon:  {1}  elim_frame : {2} ".format(
                        str(frame.ts_second),
                        time_since_last_kill, elim_frame, frame.source_name))
                return

        if time_since_last_kill >= 2:
            self.elim_count = 1
            self.elim_duration = 0
        else:
            self.elim_count = self.elim_count + 1
            self.elim_duration += time_since_last_kill
        self.emitter.emit('elim', frame, self.elim_count, self.elim_duration, self.last_death_frame)

    def too_soon_after_death(self, event_name, frame):
        time_since_last_death = frame.ts_second - self.last_death_frame
        if time_since_last_death < 0:
            time_since_last_death = 0
        if self.last_death_frame != -1 and time_since_last_death < 9:
            print(
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
        self.emitter.emit('elimed', frame)
        print("Death {1} at {0} ".format(str(frame.ts_second), frame.source_name))

    def add_spawn_room_frame(self, frame):
        self.check_if_was_queue(frame)
        self.elim_count = 0
        self.elim_duration = 0
        elim_frame_distance = frame.ts_second - self.last_hero_room_frame
        if self.last_hero_room_frame != -1 and elim_frame_distance <= 9:
            return
        print("Hero {1} Select at {0}   ".format(str(frame.ts_second), frame.source_name))
        self.emitter.emit('spawn_room', frame)
        self.last_hero_room_frame = frame.ts_second

    def check_if_was_queue(self, frame):
        if self.in_queue:
            self.emitter.emit('game_start', frame)
            self.in_queue = False

    def add_healing_frame(self, frame):
        if self.too_soon_after_death('heal', frame):
            return
        heal_frame_distance = frame.ts_second - self.last_healing_frame
        if self.last_healing_frame != -1 and heal_frame_distance < 1:
            return
        if heal_frame_distance < 6:
            self.healing_streak += 1
        else:
            self.healing_streak = 1
        print("Hero {1} Healed at {0}   ".format(str(frame.ts_second), frame.source_name))
        self.emitter.emit('healing', frame, self.healing_streak)
        self.last_healing_frame = frame.ts_second

    def add_orb_gained_frame(self, frame):
        if self.too_soon_after_death('orb', frame):
            return
        orb_frame_distance = frame.ts_second - self.last_orbing_frame
        if self.last_orbing_frame != -1 and orb_frame_distance < 1:
            return
        print("Hero {1} orbed at {0}   ".format(str(frame.ts_second), frame.source_name))
        self.emitter.emit('orbed', frame)
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
        print("Hero {1} blocking at {0}   ".format(str(frame.ts_second), frame.source_name))
        self.emitter.emit('blocking', frame, self.blocking_streak)
        self.last_blocking_frame = frame.ts_second

    def set_in_queue(self, frame):
        if self.in_queue:
            return
        self.emitter.emit('queue_start', frame)
        self.in_queue = True

    def set_in_prepare(self, frame, mode):
        self.check_if_was_queue(frame)
        if self.last_prepare_frame != -1:
            prepare_frame_distance = frame.ts_second - self.last_prepare_frame
            if prepare_frame_distance < 10:
                return
        print("Hero {1} Prepared at {0}   ".format(str(frame.ts_second), frame.source_name))
        self.emitter.emit('prepare', frame, mode)
        self.last_prepare_frame = frame.ts_second

    def add_assist_frame(self, frame):
        if self.too_soon_after_death('assist', frame):
            return
        assist_frame_distance = frame.ts_second - self.last_assist_frame
        if self.last_assist_frame != -1 and assist_frame_distance < 1:
            return
        if assist_frame_distance < 4:
            self.assist_streak += 1
        else:
            self.assist_streak = 1
        print("Hero {1} assist at {0}   ".format(str(frame.ts_second), frame.source_name))
        self.emitter.emit('assist', frame, self.assist_streak)
        self.last_assist_frame = frame.ts_second

    def add_defense_frame(self, frame):
        if self.too_soon_after_death('defense', frame):
            return
        defense_frame_distance = frame.ts_second - self.last_defense_frame
        if self.last_defense_frame != -1 and defense_frame_distance < 1:
            return
        if defense_frame_distance < 4:
            self.defense_streak += 1
        else:
            self.defense_streak = 1
        print("Hero {1} defense at {0}   ".format(str(frame.ts_second), frame.source_name))
        self.emitter.emit('defense', frame, self.defense_streak)
        self.last_defense_frame = frame.ts_second
