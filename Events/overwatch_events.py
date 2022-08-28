from typing import Tuple

from pyee.base import EventEmitter


from Ocr.frames.frame import Frame
from config.streamer_configs import get_streamer_config

overwatch_event = EventEmitter()
from Events.overwatch_events_helper import can_clip, create_clip

@overwatch_event.on('elim')
def on_elim_event(frame: Frame, count: int, duration: int, last_death):
    print("{4} Kill count: {0} seconds in: {1} last death: {2} , Duration: {3}  ".format(count, str(frame['ts_second']),
                                                                                         last_death,
                                                                                         duration, frame['source_name']))

    if not can_clip(frame, 'elim'):
        del frame
        return
    if duration != get_streamer_config(frame['source_name']).min_elims:
        del frame
        return
    created = create_clip(frame, 'elim')
    print(created)
    del frame


@overwatch_event.on('elimed')
def on_elimed_event(frame: Frame):  # you can save the frame data for a screen cap
    print("Streamer Died")
    if not can_clip(frame, 'elimed'):
        del frame
        return

    if get_streamer_config(frame['source_name']).clip_deaths:
        created = create_clip(frame, 'elimed')
        print(created)
    del frame


@overwatch_event.on('healing')
def on_healing_event(frame: Frame, duration: Tuple[int, int]):
    print("Streamer " + frame['source_name'] + " healing " + str(duration))
    if not can_clip(frame, 'healing'):
        del frame
        return

    if duration[1] != get_streamer_config(frame['source_name']).min_healing_duration:
        del frame
        return
    created = create_clip(frame, 'healing')
    print(created)
    del frame


@overwatch_event.on('queue_start')
def on_queue_start_event(frame: Frame):
    print(f"Streamer {frame['source_name']} queue_start ")
    # unclaim_monitor(frame['source_name'])
    pass


# created = create_clip(frame,'healing')


@overwatch_event.on('assist')
def on_assist_event(frame: Frame, duration: int):
    print("Streamer " + frame['source_name'] + " assist " + str(duration))
    if not can_clip(frame, 'assist'):
        del frame
        return
    if duration != get_streamer_config(frame['source_name']).min_assist_duration:
        del frame
        return
    created = create_clip(frame, 'assist')
    # print(created)
    del frame


@overwatch_event.on('defense')
def on_defense_event(frame: Frame, duration: int):
    print("Streamer " + frame['source_name'] + " defense " + str(duration))
    if not can_clip(frame, 'defense'):
        del frame
        return
    if duration != get_streamer_config(frame['source_name']).min_defense_duration:
        del frame
        return
    created = create_clip(frame, 'defense')
    # print(created)
    del frame


@overwatch_event.on('contested')
def on_contested_event(frame: Frame, duration: int):
    print("Streamer " + frame['source_name'] + " contested " + str(duration))
    if not can_clip(frame, 'contested'):
        del frame
        return
    if duration != get_streamer_config(frame['source_name']).min_contested_duration:
        del frame
        return
    created = create_clip(frame, 'contested')
    # print(created)


@overwatch_event.on('orbed')
def on_orbed_event(frame: Frame):
    print("Streamer " + frame['source_name'] + " orbed")

    # created = create_clip(frame,'orbed')
    # print(created)


@overwatch_event.on('slept')
def on_orbed_event(frame: Frame):
    print("Streamer " + frame['source_name'] + " slepting")
    if not can_clip(frame, 'slept'):
        del frame
        return

    created = create_clip(frame, 'slept')
    del frame


@overwatch_event.on('blocking')
def on_blocking_event(frame: Frame, duration: int):
    print("Streamer " + frame['source_name'] + " blocking " + str(duration))
    if not can_clip(frame, 'blocking'):
        del frame
        return
    if duration < get_streamer_config(frame['source_name']).min_blocking_duration:
        del frame
        return
    created = create_clip(frame, 'blocking')
    print(created)
    del frame


@overwatch_event.on('spawn_room')
def on_spawn_room_event(frame: Frame):
    # print("Streamer " + frame['source_name'] + " Spawning")
    # ocr: TwitchVideoFrameBuffer = get_frame_buffer(frame['source_name'])
    # clip_time_stamp = ClipTimeStamp()
    # clip_time_stamp.start = frame['ts_second']
    # clip_time_stamp.end = frame['ts_second']   + 3
    # clip_time_stamp.duration = 3
    # clip_time_stamp.type = 'elim'
    # clip_time_stamp.start_buffer = 5
    # clip_time_stamp.end_buffer = 5
    # ocr.stream_clipper.clip_request(clip_time_stamp)
    if not can_clip(frame, 'spawn_room'):
        del frame
        return
    # created = create_clip(frame,'spawn_room')
    # print(created)


@overwatch_event.on('game_start')
def on_game_start_event(frame: Frame):
    print("Streamer " + frame['source_name'] + " Game started")
    if not can_clip(frame, 'game_start'):
        del frame
        return
    # created = create_clip(frame,'game_start')
    # print(created)


@overwatch_event.on('game_end')
def on_game_end_event(frame: Frame):
    print("Streamer " + frame['source_name'] + " Game started")
    if not can_clip(frame, 'game_end'):
        del frame
        return
    # created = create_clip(frame,'game_end')
    # print(created)
