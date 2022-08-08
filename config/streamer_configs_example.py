from config.streamer_config import StreamerConfig

watch_cli_config = {  # used with added with watch and no config
    'make_clips': True,  # Set to false for just watch mode
    'min_healing_duration': 3,  # set stupid high to ignore
    'min_elims': 2,
    'min_blocking_duration': 2,
    'max_frames_to_scan_per_second': 8,
    # some people need 8, some need 4, some need 16 depending on how jank their stream is
    'min_defense_duration': 99,
    'min_assist_duration': 99,
    'stream_prefers_quality': '720p60',
    'buffer_prefers_quality': 'best',
    'wait_for_mode': False
}
streamer_configs = {
    "sapphyrelive": {
        'make_clips': True,  # Set to false for just watch mode
        'min_healing_duration': 3,  # set stupid high to ignore
        'min_elims': 2,
        'min_blocking_duration': 3,
        'min_defense_duration': 3,
        'min_assist_duration': 3,
        'clip_deaths': False,
        'stream_prefers_quality': '720p60',
        'buffer_prefers_quality': 'best',
        'max_frames_to_scan_per_second': 16,
        'wait_for_mode': True,

    }
}


def get_streamer_config(name: str) -> StreamerConfig:
    if name in streamer_configs:
        return StreamerConfig(streamer_configs[name])
    return StreamerConfig(watch_cli_config)
