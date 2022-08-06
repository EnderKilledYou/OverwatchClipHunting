from pyee.base import EventEmitter
from Ocr.frame import Frame
from config.config import make_clips
from twitch_helpers import get_twitch_api, get_broadcaster_id
overwatch_event = EventEmitter()
last_clip_time = -90
twitch = get_twitch_api()
broadcaster_id = get_broadcaster_id()


@overwatch_event.on('elim')
def on_elim_event(frame: Frame, count: int, duration: int, last_death):
    print("Kill count: {0} seconds in: {1} last death: {2} , Duration: {3}  ".format(count, str(frame.ts_second),
                                                                                     last_death,
                                                                                     duration))
    if not make_clips:
        return
    last_clip_distance = frame.ts_second - last_clip_time
    if count == 2:
        if last_clip_distance < 10:
            print("Creating clips too soon " + str(last_clip_distance))
            return
        created = twitch.create_clip(broadcaster_id)

        print(created)
    pass


@overwatch_event.on('elimed')
def on_elimed_event(frame: Frame): #you can save the frame data for a screen cap
    print("Streamer Died")
    if not make_clips:
        return
    created = twitch.create_clip(broadcaster_id)
    print(created)

    pass


@overwatch_event.on('healed')
def on_healed_event(frame: Frame, amount: int):
    print("Streamer Healed")
    if not make_clips:
        return
    created = twitch.create_clip(broadcaster_id)
    print(created)

    pass


@overwatch_event.on('healing')
def on_healing_event(frame: Frame, amount: int):
    print("Streamer healing")
    if not make_clips:
        return
    created = twitch.create_clip(broadcaster_id)
    print(created)

    pass

@overwatch_event.on('orbed')
def on_healing_event(frame: Frame, amount: int):
    print("Streamer orbed")
    if not make_clips:
        return
    # created = twitch.create_clip(broadcaster_id)
    # print(created)
    pass

@overwatch_event.on('blocking')
def on_healing_event(frame: Frame, amount: int):
    print("Streamer blocking")
    if not make_clips:
        return
    # created = twitch.create_clip(broadcaster_id)
    # print(created)

    pass

@overwatch_event.on('spawn_room')
def on_spawn_room_event(frame: Frame):
    print("Streamer Spawning")
    if not make_clips:
        return
    created = twitch.create_clip(broadcaster_id)
    print(created)

    pass


@overwatch_event.on('game_start')
def on_game_start_event(frame: Frame):
    print("Streamer Game started")
    if not make_clips:
        return
    created = twitch.create_clip(broadcaster_id)
    print(created)

    pass


@overwatch_event.on('game_end')
def on_game_end_event(frame: Frame):
    print("Streamer Game started")
    if not make_clips:
        return
    created = twitch.create_clip(broadcaster_id)
    print(created)

    pass
