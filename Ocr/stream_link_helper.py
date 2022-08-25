import traceback

from streamlink import NoPluginError, Streamlink, PluginError
from streamlink.plugins.twitch import TwitchHLSStream
from typing import Dict, Tuple

from cloud_logger import cloud_logger


class StreamLinkHelper:
    sl_session = Streamlink()

    @staticmethod
    def get_best_stream(broadcaster: str) -> TwitchHLSStream:
        try:
            streams = StreamLinkHelper.sl_session.streams('https://www.twitch.tv/{0}'.format(broadcaster))
        except NoPluginError as npe:
            print("no support for that stream")
            return None
        except PluginError as pe:
            print("Probably twitch timed out")
            return None
        except BaseException as e:
            traceback.print_exc()
            return None
        if 'best' not in streams:
            return None

        return StreamLinkHelper._parse_best_stream(streams)

    @staticmethod
    def _parse_best_stream(streams: Dict[str, TwitchHLSStream]) -> Tuple[TwitchHLSStream, str]:
        cloud_logger()
        ocr_stream = streams['best']
        items = []

        if '480p60' in streams:
            return streams['480p60'], '480p60'
        if '720p60' in streams:
            return streams['720p60'], '720p60'
        if '480p' in streams:
            return streams['480p'], '480p'

        for stream_res in streams:
            if not stream_res.endswith('p60'):
                continue
            items.append((streams[stream_res], stream_res))
        try:
            return items.pop()
        except:
            return ocr_stream, "best"
