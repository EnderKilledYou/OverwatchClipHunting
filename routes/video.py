import re

import requests
from flask import request, Response, Blueprint

video = Blueprint('video', __name__)

from twitchdl.commands.download import get_clip_authenticated_url

from Database.Twitch.twitch_clip_instance import get_twitch_clip_video_id_by_id
from Database.Twitch.twitch_clip_tag import TwitchClipTag, get_tag_and_bag_by_id
from Ocr.frames.ordered_frame_aggregator import OrderedFrameAggregator
from google_cloud_helpers.google_cloud_helper import get_blob_by_path
from routes.frame_watcher_manager import clip_frame_watchers
from routes.route_cache import cache


@video.after_request
def after_request(response):
    response.headers.add('Accept-Ranges', 'bytes')
    return response


def get_chunk(full_path, byte1=None, byte2=None):
    blob = get_blob_by_path(full_path)
    file_size = blob.size
    start = 0

    if byte1 < file_size:
        start = byte1
    if byte2:
        length = byte2 + 1 - byte1
    else:
        length = file_size - start

    with blob.open('rb') as f:
        f.seek(start)
        chunk = f.read(length)
    return chunk, start, length, file_size


@video.route('/clip/<clip_id>')
def get_clip(clip_id: int):
    id_url = f'clip{clip_id}url'
    if cache.has(id_url):
        url = cache.get(id_url)
    else:
        video_id = get_twitch_clip_video_id_by_id(clip_id)
        url = get_clip_authenticated_url(video_id, "source")
        cache.set(url, url, 1000)

    range_header = request.headers.get('Range', None)
    byte1, byte2 = 0, None
    headers = {}
    if range_header:
        match = re.search(r'(\d+)-(\d*)', range_header)
        groups = match.groups()

        if groups[0]:
            byte1 = int(groups[0])
        if groups[1]:
            byte2 = int(groups[1])
        headers = {"Range": f"bytes={byte1}-{byte2}"}

    with requests.get(url, headers=headers, stream=True) as r:
        return r.content


@video.route('/tag_video/<tag_id>')
def get_file(tag_id: int):
    try:
        tag: TwitchClipTag = get_tag_and_bag_by_id(int(tag_id))
        if not tag:
            return
        if tag.file_name is None:
            return

    except:
        return

    range_header = request.headers.get('Range', None)
    byte1, byte2 = 0, None
    if range_header:
        match = re.search(r'(\d+)-(\d*)', range_header)
        groups = match.groups()

        if groups[0]:
            byte1 = int(groups[0])
        if groups[1]:
            byte2 = int(groups[1])

    chunk, start, length, file_size = get_chunk(tag.file_name, byte1, byte2)
    resp = Response(chunk, 206, mimetype='video/mp4',
                    content_type='video/mp4', direct_passthrough=True)
    resp.headers.add('Content-Range', 'bytes {0}-{1}/{2}'.format(start, start + length - 1, file_size))
    return resp


# frame_watchers[streamer] = OrderedFrameAggregator(overwatch_event)


@video.route('/clip/<clip_token>')
def clip_token(clip_token: str, streamer: str):
    if streamer not in clip_frame_watchers:
        return
    frame_watcher: OrderedFrameAggregator
    (token, frame_watcher) = clip_frame_watchers[streamer]
    if token != clip_token:
        return
