import os
from typing import List

from Database.live_twitch_instance import LiveTwitchInstance
from Database.monitor import get_claimed_count, claim_monitor, get_monitor_by_name, reset_for_claim
from cloud_logger import cloud_logger, cloud_message


def claim_one_monitor( streams: List[LiveTwitchInstance]):
    cloud_logger()
    claimed_count = get_claimed_count()
    if claimed_count >= max_active_monitors:
        cloud_message("No space to start new streamers")
        return

    for stream in streams:
        user_login = stream.user_login
        claimed = claim_monitor(user_login)
        if not claimed:
            continue
        monitor = get_monitor_by_name(user_login)
        reset_for_claim(user_login)

        return monitor


if 'MAX_ACTIVE_MONITORS' not in os.environ:
    max_active_monitors = 5
else:
    max_active_monitors = int(os.environ['MAX_ACTIVE_MONITORS'])
