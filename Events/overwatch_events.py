from typing import Tuple

from pyee.base import EventEmitter

from Events.overwatch_events_helper import can_clip, create_clip
from Ocr.frames.frame import Frame
from config.streamer_configs import get_streamer_config

overwatch_event = EventEmitter()


@overwatch_event.on('elim')
def on_elim_event(frame: Frame, count: int, duration: int, last_death):
    print("{4} Kill count: {0} seconds in: {1} last death: {2} , Duration: {3}  ".format(count, str(frame.ts_second),
                                                                                         last_death,
                                                                                         duration, frame.source_name))
    # ocr: TwitchVideoFrameBuffer = get_frame_buffer(frame.source_name)
    # config = get_streamer_config(frame.source_name)
    # clip_time_stamp = ClipTimeStamp()
    # clip_time_stamp.start = frame.ts_second
    # clip_time_stamp.end = frame.ts_second + duration + 1
    # clip_time_stamp.duration = duration
    # clip_time_stamp.type = 'elim'
    # clip_time_stamp.start_buffer = config.buffer_elim_clip_before
    # clip_time_stamp.end_buffer = config.buffer_elim_clip_after
    # ocr.stream_clipper.clip_request(clip_time_stamp)
    if not can_clip(frame, 'elim'):
        return
    if duration != get_streamer_config(frame.source_name).min_elims:
        return
    created = create_clip(frame, 'elim')
    print(created)


@overwatch_event.on('elimed')
def on_elimed_event(frame: Frame):  # you can save the frame data for a screen cap
    print("Streamer Died")
    if not can_clip(frame, 'elimed'):
        return

    if get_streamer_config(frame.source_name).clip_deaths:
        created = create_clip(frame, 'elimed')
        print(created)


@overwatch_event.on('healing')
def on_healing_event(frame: Frame, duration: Tuple[int,int]):
    print("Streamer " + frame.source_name + " healing " + str(duration))
    if not can_clip(frame, 'healing'):
        return

    if duration[1] != get_streamer_config(frame.source_name).min_healing_duration:
        return
    created = create_clip(frame, 'healing')
    print(created)


@overwatch_event.on('queue_start')
def on_queue_start_event(frame: Frame):
    pass


# created = create_clip(frame,'healing')


@overwatch_event.on('assist')
def on_assist_event(frame: Frame, duration: int):
    print("Streamer " + frame.source_name + " assist " + str(duration))
    if not can_clip(frame, 'assist'):
        return
    if duration != get_streamer_config(frame.source_name).min_assist_duration:
        return
    created = create_clip(frame, 'assist')
    # print(created)


@overwatch_event.on('defense')
def on_defense_event(frame: Frame, duration: int):
    print("Streamer " + frame.source_name + " defense " + str(duration))
    if not can_clip(frame, 'defense'):
        return
    if duration != get_streamer_config(frame.source_name).min_defense_duration:
        return
    created = create_clip(frame, 'defense')
    # print(created)


@overwatch_event.on('contested')
def on_contested_event(frame: Frame, duration: int):
    print("Streamer " + frame.source_name + " contested " + str(duration))
    if not can_clip(frame, 'contested'):
        return
    if duration != get_streamer_config(frame.source_name).min_contested_duration:
        return
    created = create_clip(frame, 'contested')
    # print(created)


@overwatch_event.on('orbed')
def on_orbed_event(frame: Frame):
    print("Streamer " + frame.source_name + " orbed")

    # created = create_clip(frame,'orbed')
    # print(created)


@overwatch_event.on('slept')
def on_orbed_event(frame: Frame):
    print("Streamer " + frame.source_name + " slepting")
    if not can_clip(frame, 'slept'):
        return

    created = create_clip(frame, 'slept')


@overwatch_event.on('blocking')
def on_blocking_event(frame: Frame, duration: int):
    print("Streamer " + frame.source_name + " blocking " + str(duration))
    if not can_clip(frame, 'blocking'):
        return
    if duration < get_streamer_config(frame.source_name).min_blocking_duration:
        return
    created = create_clip(frame, 'blocking')
    print(created)


@overwatch_event.on('spawn_room')
def on_spawn_room_event(frame: Frame):
    # print("Streamer " + frame.source_name + " Spawning")
    # ocr: TwitchVideoFrameBuffer = get_frame_buffer(frame.source_name)
    # clip_time_stamp = ClipTimeStamp()
    # clip_time_stamp.start = frame.ts_second
    # clip_time_stamp.end = frame.ts_second   + 3
    # clip_time_stamp.duration = 3
    # clip_time_stamp.type = 'elim'
    # clip_time_stamp.start_buffer = 5
    # clip_time_stamp.end_buffer = 5
    # ocr.stream_clipper.clip_request(clip_time_stamp)
    if not can_clip(frame, 'spawn_room'):
        return
    # created = create_clip(frame,'spawn_room')
    # print(created)


@overwatch_event.on('game_start')
def on_game_start_event(frame: Frame):
    print("Streamer " + frame.source_name + " Game started")
    if not can_clip(frame, 'game_start'):
        return
    # created = create_clip(frame,'game_start')
    # print(created)


@overwatch_event.on('game_end')
def on_game_end_event(frame: Frame):
    print("Streamer " + frame.source_name + " Game started")
    if not can_clip(frame, 'game_end'):
        return
    # created = create_clip(frame,'game_end')
    # print(created)
