from typing import List

from Database.live_twitch_instance import LiveTwitchInstance
from Database.monitor import get_claimed_count, claim_monitor, get_monitor_by_name
from cloud_logger import cloud_logger, cloud_message


class ClaimMonitor:
    def __init__(self):
        self.max_active_monitors = 5

    def claim_one_monitor(self, streams: List[LiveTwitchInstance]):
        cloud_logger()
        claimed_count = get_claimed_count()
        if claimed_count >= self.max_active_monitors:
            cloud_message("No space to start new streamers")
            return

        for stream in streams:
            claimed = claim_monitor(stream['user_login'])
            if not claimed:
                continue
            monitor = get_monitor_by_name(stream['user_login'])
            return monitor
        return None
