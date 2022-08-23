from typing import Optional, List

from dateutil.parser import isoparse

from cloud_logger import cloud_logger
from routes.clips.clips import sharp
from routes.clips.parse_broadcaster_id import parse_broadcaster_id
from twitch_helpers.twitch_helpers import get_twitch_api


@sharp.function()
def search_twitch_clips(broadcaster: Optional[str] = None,
                        game_id: Optional[str] = None,
                        clip_id: Optional[List[str]] = None,

                        ended_at: Optional[str] = None,
                        started_at: Optional[str] = None,
                        after_cursor: Optional[str] = None,
                        before_cursor: Optional[str] = None):
    twitch_api = get_twitch_api(
    )
    try:
        cloud_logger()
        if started_at is not None:
            started_at = isoparse(started_at)
        if ended_at is not None:
            ended_at = isoparse(ended_at)
        broadcaster_id = parse_broadcaster_id(broadcaster, twitch_api)
        result = twitch_api.get_clips(broadcaster_id=broadcaster_id,
                                      game_id=game_id,
                                      clip_id=clip_id,
                                      before=before_cursor,
                                      after=after_cursor,
                                      ended_at=ended_at,
                                      started_at=started_at)
    except BaseException as b:
        return {"success": False, "error": str(b)}
    if not result:
        return {"success": False, "error": "something fucky no result maybe twitch ded?"}
    return {"success": True, 'api_result': result}
