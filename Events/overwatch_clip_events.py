from typing import Tuple

from pyee.base import EventEmitter

overwatch_clips_event = EventEmitter()

from Ocr.frames.frame import Frame

from Database.Twitch.twitch_clip_tag import add_twitch_clip_tag_request


@overwatch_clips_event.on('elim')
def on_elim_event(frame: Frame, count: int, duration: int, last_death):
    print("{4} Kill count: {0} seconds in: {1} last death: {2} , Duration: {3}  ".format(count, str(frame.ts_second),
                                                                                         last_death,
                                                                                         duration, frame['source_name']))
    add_twitch_clip_tag_request(frame['clip_id'], 'elim', count, duration, frame.ts_second)


@overwatch_clips_event.on('elimed')
def on_elimed_event(frame: Frame):  # you can save the frame data for a screen cap
    print("Streamer Died")
    add_twitch_clip_tag_request(frame['clip_id'], 'elimed', 1, 1, frame.ts_second)


@overwatch_clips_event.on('healing')
def on_healing_event(frame: Frame, duration: Tuple[int, int]):
    print(f"Streamer {frame['source_name']} healing {str(duration[0])} {str(duration[1])}")
    add_twitch_clip_tag_request(frame['clip_id'], 'healing', duration[1], duration[2], duration[0])


@overwatch_clips_event.on('queue_start')
def on_queue_start_event(frame: Frame):
    print("Streamer " + frame['source_name'] + " queue_start ")
    add_twitch_clip_tag_request(frame['clip_id'], 'queue_start', 1, 1, frame.ts_second)


@overwatch_clips_event.on('assist')
def on_assist_event(frame: Frame, duration: int):
    print("Streamer " + frame['source_name'] + " assist " + str(duration))
    add_twitch_clip_tag_request(frame['clip_id'], 'assist', 1, duration, frame.ts_second)


@overwatch_clips_event.on('defense')
def on_defense_event(frame: Frame, duration: int):
    print("Streamer " + frame['source_name'] + " defense " + str(duration))
    add_twitch_clip_tag_request(frame['clip_id'], 'defense', 1, duration, frame.ts_second)


@overwatch_clips_event.on('orbed')
def on_orbed_event(frame: Frame):
    print("Streamer " + frame['source_name'] + " orbed")
    add_twitch_clip_tag_request(frame['clip_id'], 'orbed', 1, 1, frame.ts_second)


@overwatch_clips_event.on('slept')
def on_orbed_event(frame: Frame):
    print("Streamer " + frame['source_name'] + " slepting")
    add_twitch_clip_tag_request(frame['clip_id'], 'slept', 1, 1, frame.ts_second)


@overwatch_clips_event.on('blocking')
def on_blocking_event(frame: Frame, duration: int):
    print("Streamer " + frame['source_name'] + " blocking " + str(duration))
    add_twitch_clip_tag_request(frame['clip_id'], 'blocking', 1, duration, frame.ts_second)


@overwatch_clips_event.on('spawn_room')
def on_spawn_room_event(frame: Frame):
    add_twitch_clip_tag_request(frame['clip_id'], 'spawn_room', 1, 1, frame.ts_second)
    pass


@overwatch_clips_event.on('game_start')
def on_game_start_event(frame: Frame):
    print("Streamer " + frame['source_name'] + " Game started")
    add_twitch_clip_tag_request(frame['clip_id'], 'game_start', 1, 1, frame.ts_second)


@overwatch_clips_event.on('game_end')
def on_game_end_event(frame: Frame):
    print("Streamer " + frame['source_name'] + " Game started")
    add_twitch_clip_tag_request(frame['clip_id'], 'game_end', 1, 1, frame.ts_second)
