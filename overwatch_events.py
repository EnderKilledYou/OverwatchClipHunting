from pyee.base import EventEmitter

from Ocr.frame import Frame
from config.config import min_healing_duration, min_elims, min_assist_duration, min_defense_duration, \
    min_blocking_duration
from overwatch_events_helper import create_clip, can_clip

overwatch_event = EventEmitter()


@overwatch_event.on('elim')
def on_elim_event(frame: Frame, count: int, duration: int, last_death):
    print("{4} Kill count: {0} seconds in: {1} last death: {2} , Duration: {3}  ".format(count, str(frame.ts_second),
                                                                                         last_death,
                                                                                         duration, frame.source_name))
    if not can_clip(frame, 'elim'):
        return

    if count == min_elims:
        created = create_clip(frame)
        last_clip_time = frame.ts_second
        print(created)
    pass


@overwatch_event.on('elimed')
def on_elimed_event(frame: Frame):  # you can save the frame data for a screen cap
    print("Streamer Died")
    if not can_clip(frame, 'elimed'):
        return
    created = create_clip(frame)
    print(created)

    pass


@overwatch_event.on('healing')
def on_healing_event(frame: Frame, duration: int):
    print("Streamer " + frame.source_name + " healing " + str(duration))
    if not can_clip(frame,'healing'):
        return
    if duration < min_healing_duration:
        return
    created = create_clip(frame, 'healing')
    print(created)
@overwatch_event.on('queue_start')
def on_queue_start_event(frame: Frame):
    print("Streamer " + frame.source_name + " queue_start ")



@overwatch_event.on('assist')
def on_assist_event(frame: Frame, duration: int):
    print("Streamer " + frame.source_name + " assist " + str(duration))
    if not can_clip(frame, 'assist'):
        return
    if duration < min_assist_duration:
        return
    created = create_clip(frame)
    # print(created)


@overwatch_event.on('defense')
def on_defense_event(frame: Frame, duration: int):
    print("Streamer " + frame.source_name + " defense " + str(duration))
    if not can_clip(frame, 'defense'):
        return
    if duration < min_defense_duration:
        return
    created = create_clip(frame)
    # print(created)


@overwatch_event.on('orbed')
def on_orbed_event(frame: Frame):
    print("Streamer " + frame.source_name + " orbed")
    if not can_clip(frame, 'orbed'):
        return

    created = create_clip(frame)
    # print(created)


@overwatch_event.on('slept')
def on_orbed_event(frame: Frame):
    print("Streamer " + frame.source_name + " slepting")
    if not can_clip(frame, 'slept'):
        return

    created = create_clip(frame)
    # print(created)


@overwatch_event.on('blocking')
def on_blocking_event(frame: Frame, duration: int):
    print("Streamer " + frame.source_name + " blocking " + str(duration))
    if not can_clip(frame, 'blocking'):
        return
    if duration < min_blocking_duration:
        return
    # created = create_clip(frame)
    # print(created)


@overwatch_event.on('spawn_room')
def on_spawn_room_event(frame: Frame):
    print("Streamer " + frame.source_name + " Spawning")
    if not can_clip(frame, 'spawn_room'):
        return
    # created = create_clip(frame)
    # print(created)


@overwatch_event.on('game_start')
def on_game_start_event(frame: Frame):
    print("Streamer " + frame.source_name + " Game started")
    if not can_clip(frame, 'game_start'):
        return
    # created = create_clip(frame)
    # print(created)


@overwatch_event.on('game_end')
def on_game_end_event(frame: Frame):
    print("Streamer " + frame.source_name + " Game started")
    if not can_clip(frame, 'game_end'):
        return
    # created = create_clip(frame)
    # print(created)
