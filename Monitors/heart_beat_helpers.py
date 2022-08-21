import os
from typing import List

import cloud_logger
from Database.live_twitch_instance import LiveTwitchInstance
from Database.monitor import claim_monitor, get_monitor_by_name, reset_for_claim


def claim_one_monitor(streams: List[LiveTwitchInstance], claimed_count: int):
    cloud_logger.cloud_logger()

    if claimed_count >= max_active_monitors :
        cloud_logger.cloud_message("No space to start new streamers")
        return

    for stream in streams:
        if stream.game_name.lower().startswith("overwatch"):
            user_login = stream.user_login
            claimed = claim_monitor(user_login)
            if not claimed:
                continue
            cloud_logger.cloud_message("Claimed One" + user_login)
            monitor = get_monitor_by_name(user_login)
            reset_for_claim(user_login)

            return monitor, stream.game_name


if 'MAX_ACTIVE_MONITORS' not in os.environ:
    max_active_monitors = os.cpu_count()
else:
    max_active_monitors = int(os.environ['MAX_ACTIVE_MONITORS'])
