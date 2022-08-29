from config.streamer_config import StreamerConfig

watch_cli_config = {  # used with added with watch and no config
       'make_clips': True,  # Set to false for just watch mode
        'min_healing_duration': 8,  # set stupid high to ignore
        'min_elims': 3,
        'min_blocking_duration': 10,
        'min_defense_duration': 10,
        'min_assist_duration':4,
        'clip_deaths': False,
        'stream_prefers_quality': '720p60',
        'buffer_prefers_quality': 'best',
        'max_frames_to_scan_per_second': 16,
        'wait_for_mode': False,
}
streamer_configs = {

}


def get_streamer_config(name: str) -> StreamerConfig:
    if name in streamer_configs:
        return StreamerConfig(streamer_configs[name])
    return StreamerConfig(watch_cli_config)
