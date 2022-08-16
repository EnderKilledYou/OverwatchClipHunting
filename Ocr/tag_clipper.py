import os
import tempfile
from os.path import abspath

import ffmpeg

from Database.Twitch.twitch_clip_instance import get_twitch_clip_instance_by_id, TwitchClipInstance



from something_manager import ThreadedManager
class TagClipper(ThreadedManager):
    def __init__(self):
        super(TagClipper, self).__init__(2, False)

    def _do_work(self, job):
        (item, file) = job
        try:

            clip: TwitchClipInstance = get_twitch_clip_instance_by_id(item.clip_id)
            storage_path = self.get_storage_path(clip)

            for section in item.clip_parts:
                file_name = next(tempfile._get_candidate_names()) + '.mp4'
                out_file = storage_path + os.sep + file_name
                gloud_file = get_clip_path(clip) + file_name
                trim(file, out_file, section.clip_start, section.clip_end)
                update_tag_and_bag_filename(section.id, gloud_file)
                copy_to_cloud(out_file, gloud_file)
                os.unlink(out_file)

            item.return_queue.put((clip.id,))
        except BaseException as e:
            item.return_queue.put((clip.id, str(e)))


from Database.Twitch.update_tag_and_bag_filename import update_tag_and_bag_filename
from startup_file import copy_to_cloud




def get_clip_path(clip: TwitchClipInstance):
    return f'/videos{os.sep}{clip.broadcaster_name}{os.sep}{str(clip.created_at.year)}{os.sep}{str(clip.created_at.month)}{os.sep}{str(clip.created_at.day)}{os.sep}'


def get_storage_path(clip: TwitchClipInstance):
    storage_path = abspath(get_clip_path(get_clip_path(clip)))

    if not os.path.exists(storage_path):
        os.makedirs(storage_path)
    return storage_path


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
