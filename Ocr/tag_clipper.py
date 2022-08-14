import os
import tempfile
from os.path import abspath

import ffmpeg
import requests
import twitchdl.download
from twitchdl.commands.download import _download_clip
import config.config
from Ocr.re_scaner import tmp_path
from Ocr.tag_clipper_request import TagClipperRequest
from something_manager import ThreadedManager
from twitch.twitch_clip_instance import get_twitch_clip_instance_by_id
from twitch.twitch_clip_tag import update_tag_and_bag_filename


class Args:
    def __init__(self, video_id: str, out_file: str):
        self.quality = "source"
        self.output = out_file
        self.video = video_id
        self.start = None
        self.end = None
        self.overwrite = True


class TagClipper(ThreadedManager):
    def __init__(self):
        super(TagClipper, self).__init__(2, False)

    def _stream_to_file(self, url, path):
        _download_clip(url, Args(url, path))
        return
        twitchdl.CLIENT_ID = config.config.consumer_key
        twitchdl.download.download_file()
        response = requests.get(url, stream=True, timeout=60)
        size = 0
        with open(path, 'wb') as target:
            for chunk in response.iter_content(chunk_size=8096):
                target.write(chunk)
                size += len(chunk)

        return size

    def _download(self, url: str):
        self.file_name = tmp_path + os.sep + next(tempfile._get_candidate_names()) + '.mp4'
        size = self._stream_to_file(url, self.file_name)
        return self.file_name, size

    def _do_work(self, item: TagClipperRequest):
        try:
            file_info = self._download(item.video_id)
            file = file_info[0]
            clip = get_twitch_clip_instance_by_id(item.clip_id)
            storage_path = abspath(
                f'./videos{os.sep}{clip.broadcaster_name}{os.sep}{str(clip.created_at.year)}{os.sep}{str(clip.created_at.month)}{os.sep}{str(clip.created_at.day)}{os.sep}')
            if not os.path.exists(storage_path):
                os.makedirs(storage_path)
            probe = ffmpeg.probe(file)
            video_info = next(s for s in probe['streams'] if s['codec_type'] == 'video')
            fps = int(video_info['r_frame_rate'].split('/')[0])
            for section in item.clip_parts:
                out_file = storage_path + os.sep + next(tempfile._get_candidate_names()) + '.mp4'
                trim(file, out_file, section.clip_start, section.clip_end)
                # ffmpeg.input(file).trim(start_frame=section.clip_start * fps, end_frame=section.clip_end * fps).output(
                #    out_file).run()
                update_tag_and_bag_filename(section.id, out_file)

            os.unlink(file)
            item.return_queue.put((clip.id,))
        except BaseException as e:
            item.return_queue.put((clip.id, str(e)))


def trim(input_path, output_path, start=30, end=60):
    input_stream = ffmpeg.input(input_path)

    vid = (
        input_stream.video
        .trim(start=start, end=end)
        .setpts('PTS-STARTPTS')
    )
    aud = (
        input_stream.audio
        .filter_('atrim', start=start, end=end)
        .filter_('asetpts', 'PTS-STARTPTS')
    )

    joined = ffmpeg.concat(vid, aud, v=1, a=1).node
    output = ffmpeg.output(joined[0], joined[1], output_path)
    output.run()
