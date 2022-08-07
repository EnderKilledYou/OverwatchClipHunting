from pyee.base import EventEmitter

import overwatch_events_helper
from Ocr.frame import Frame
from overwatch_events_helper import create_clip, can_clip
from twitch_helpers import get_twitch_api, get_broadcaster_id

overwatch_event = EventEmitter()



@overwatch_event.on('elim')
def on_elim_event(frame: Frame, count: int, duration: int, last_death):
    print("Kill count: {0} seconds in: {1} last death: {2} , Duration: {3}  ".format(count, str(frame.ts_second),
                                                                                     last_death,
                                                                                     duration))
    if not can_clip(frame):
        return

    if count == 2:
        created = create_clip(frame)
        last_clip_time = frame.ts_second
        print(created)
    pass


@overwatch_event.on('elimed')
def on_elimed_event(frame: Frame):  # you can save the frame data for a screen cap
    print("Streamer Died")
    if not can_clip(frame):
        return
    created = create_clip(frame)
    print(created)

    pass


@overwatch_event.on('healed')
def on_healed_event(frame: Frame, amount: int):
    print("Streamer Healed")
    if not can_clip(frame):
        return
    created = create_clip(frame)
    print(created)

    pass


@overwatch_event.on('healing')
def on_healing_event(frame: Frame, amount: int):
    print("Streamer healing " + str(amount))
    if not can_clip(frame):
        return
    created = create_clip(frame)
    print(created)

    pass

@overwatch_event.on('assist')
def on_assist_event(frame: Frame):
    print("Streamer assist")
    if not can_clip(frame):
        return
    created = create_clip(frame)
    # print(created)
    pass
@overwatch_event.on('defense')
def on_defense_event(frame: Frame):
    print("Streamer defense")
    if not can_clip(frame):
        return
    created = create_clip(frame)
    # print(created)
    pass
@overwatch_event.on('orbed')
def on_orbed_event(frame: Frame):
    print("Streamer orbed")
    if not can_clip(frame):
        return
    created = create_clip(frame)
    # print(created)
    pass


@overwatch_event.on('blocking')
def on_blocking_event(frame: Frame):
    print("Streamer blocking")
    if not can_clip(frame):
        return
    # created = create_clip(frame)
    # print(created)

    pass


@overwatch_event.on('spawn_room')
def on_spawn_room_event(frame: Frame):
    print("Streamer Spawning")
    if not can_clip(frame):
        return
    # created = create_clip(frame)
    # print(created)

    pass


@overwatch_event.on('game_start')
def on_game_start_event(frame: Frame):
    print("Streamer Game started")
    if not can_clip(frame):
        return
    # created = create_clip(frame)
    # print(created)

    pass


@overwatch_event.on('game_end')
def on_game_end_event(frame: Frame):
    print("Streamer Game started")
    if not can_clip(frame):
        return
    # created = create_clip(frame)
    # print(created)

    pass
