import os
import re

from flask import request, Response, Blueprint

from Database.MissingRecordError import MissingRecordError
from Database.Twitch.twitch_clip_tag import TwitchClipTag, get_tag_and_bag_by_id
from startup_file import get_blob_by_path

video = Blueprint('video', __name__)


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
        chunk = f.read_db_from_cloud(length)
    return chunk, start, length, file_size


@video.route('/tag_video/<tag_id>')
def get_file(tag_id: int):
    try:
        tag: TwitchClipTag = get_tag_and_bag_by_id(int(tag_id))
        if not tag:
            return
        if tag.file_name is None:
            return
    except MissingRecordError:
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
