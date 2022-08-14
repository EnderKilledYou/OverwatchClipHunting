import traceback

from streamlink import NoPluginError, Streamlink
from streamlink.plugins.twitch import TwitchHLSStream
from typing import Dict


class StreamLinkHelper:
    sl_session = Streamlink()

    @staticmethod
    def get_best_stream(broadcaster: str) -> TwitchHLSStream:
        try:
            streams = StreamLinkHelper.sl_session.streams('https://www.twitch.tv/{0}'.format(broadcaster))
        except NoPluginError as npe:
            print("no support for that stream")
            return None
        except BaseException as e:
            traceback.print_exc()
            return None
        if 'best' not in streams:
            return None

        return StreamLinkHelper._parse_best_stream(streams)

    @staticmethod
    def _parse_best_stream(streams: Dict[str, TwitchHLSStream]) -> TwitchHLSStream:
        ocr_stream = streams['best']
        items = []
        for stream_res in streams:
            if not stream_res.endswith('p60'):
                continue
            items.append((streams[stream_res], stream_res))
        if len(items) < 1:
            return ocr_stream
        items_ = items[:-1][0]
        return items_[0]
