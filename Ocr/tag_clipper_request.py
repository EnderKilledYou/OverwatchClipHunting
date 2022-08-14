from queue import Queue
from typing import List

from twitch.twitch_clip_tag import TwitchClipTag


class TagClipperRequest:
    clip_id: int
    
    clip_parts: List[TwitchClipTag]
    broadcaster: str
    video_id:str
    
    def __init__(self, clip_id,  clip_parts: List[TwitchClipTag], broadcaster: str ,video_id:str,return_queue=None):

        self.return_queue = return_queue
        self.video_id = video_id
        self.broadcaster = broadcaster

        self.clip_parts = clip_parts
        self.clip_id = clip_id
