from Database.Twitch.twitch_clip_instance import TwitchClipInstance, fix_vod_and_duration
from monitor_manager import MonitorManager
from twitch_helpers import get_twitch_api


def test_query():
    man = MonitorManager()
    man.heart_beat()
    return
    twitch = get_twitch_api()
    for clip in TwitchClipInstance.query.filter_by():
        api_data_result = twitch.get_clips(clip_id=clip.video_id)
        if "data" in api_data_result and len(api_data_result["data"]) > 0:
            api_data = api_data_result["data"][0]
            fix_vod_and_duration(api_data)


