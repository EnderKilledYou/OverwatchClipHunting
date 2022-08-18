from random import shuffle

from cloud_logger import cloud_logger


class TwitchFarm:
    def set_farm_twitch_mode(self, mode: bool):
        cloud_logger()
        self._farm_twitch_mode = mode

    def _farm_twitch(self, twitch_api):
        cloud_logger()
        count = self.max_twitch_farms - len(self._monitors)
        if count < 1:
            return
        streams = twitch_api.get_streams(game_id="488552", language=['en'], first=100)
        if not streams or 'data' not in streams or len(streams['data']) == 0:
            return
        shuffle(streams['data'])
        for i in range(0, count):
            stream = streams['data'].pop()
            self.add_stream_to_monitor(stream['user_login'])
