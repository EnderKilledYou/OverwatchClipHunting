import traceback

from streamlink import NoPluginError, Streamlink, PluginError
from streamlink.plugins.twitch import TwitchHLSStream
from typing import Dict, Tuple

from cloud_logger import cloud_logger


class StreamLinkHelper:
    sl_session = Streamlink()

    @staticmethod
    def get_best_stream(broadcaster: str) -> Tuple[str, str]:
        try:
            streams = StreamLinkHelper.sl_session.streams('https://www.twitch.tv/{0}'.format(broadcaster))
        except NoPluginError as npe:
            print(f"no support for that stream {broadcaster}")
            return None
        except PluginError as pe:
            print(f"Probably twitch timed out {broadcaster} {str(pe)}")
            return None
        except BaseException as e:
            traceback.print_exc()
            return None
        if 'best' not in streams:
            return None

        best_stream = StreamLinkHelper._parse_best_stream(streams)

        keys = list(streams.keys())
        for item in keys:
            del streams[item]
        del keys

        return best_stream

    @staticmethod
    def _parse_best_stream(streams: Dict[str, TwitchHLSStream]) -> Tuple[str, str]:
        cloud_logger()
        ocr_stream = streams['best']
        return ocr_stream.url, "best"


        if '480p60' in streams:
            return streams['480p60'].url, '480p60'
        if '720p60' in streams:
            return streams['720p60'].url, '720p60'
        if '480p' in streams:
            return streams['480p'].url, '480p'

        for stream_res in streams:
            if not stream_res.endswith('p60'):
                continue
            items.append((streams[stream_res], stream_res))
        try:
            pop = items.pop()
            items.clear()
            return pop
        except:
            return ocr_stream.url, "best"
