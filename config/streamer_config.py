class StreamerConfig:
    make_clips = True  # Set to false for just watch mode
    min_healing_duration = 4  # set stupid high to ignore
    min_elims = 4
    min_blocking_duration = 3
    min_defense_duration = 5
    min_assist_duration = 4
    min_contested_duration = 3
    stream_prefers_quality = '720p60'
    wait_for_mode = True
    buffer_prefers_quality = 'best'
    buffer_elim_clip_after = 5
    buffer_elim_clip_before = 5
    buffer_data = False
    clip_deaths = False

    def __init__(self,defaults = {}):

        for key in defaults:
            setattr(self, key, defaults[key])
