from app import app
import json
import os

import sys

import time
from os.path import abspath

from dateutil.parser import isoparse

from Database.Twitch.update_tag_and_bag_filename import update_tag_and_bag_filename

from startup_file import copy_to_cloud
from Database.Twitch.twitch_clip_instance import get_twitch_clip_instance_by_id, TwitchClipInstance, \
    update_twitch_clip_instance_filename
from Database.Twitch.get_tag_and_bag import get_tag_and_bag_by_clip_id
from Database.Twitch.twitch_clip_instance_scan_job import update_scan_job_percent, update_scan_job_error, \
    update_scan_job_in_subclip, update_scan_job_in_deepface, update_scan_job_in_deepfacequeue
from cloud_logger import cloud_logger, cloud_error_logger
from generic_helpers.get_unix_time import temp_name

from generic_helpers.something_manager import ThreadedManager


class TagClipper(ThreadedManager):
    def __init__(self):
        super(TagClipper, self).__init__(3, False)

    def __str__(self):
        return f"TagClipper "

    def __json__(self):
        to_dict = {'name': 'TagClipper'}
        return to_dict

    def __repr__(self):
        try:
            return json.dumps({})
        except:
            print("TagClipper convert to json failed")
            return json.dumps(['TagClipper'])
    
    def _do_work(self, job):
        cloud_logger()
        (clip_id, file, scan_job_id) = job

        try:
            update_scan_job_in_subclip(scan_job_id)
            clip: TwitchClipInstance = get_twitch_clip_instance_by_id(clip_id)
            storage_path = get_storage_path(clip)
            clip_parts = get_tag_and_bag_by_clip_id(clip_id)
            update_scan_job_percent(scan_job_id, 0)
            i = 0.0
            total = float(len(clip_parts))

            for section in clip_parts:
                percent = i / total
                update_scan_job_percent(scan_job_id, percent)
                i += 1
                file_name = temp_name() + '.mp4'
                out_file = storage_path + os.sep + file_name
                gloud_file = get_clip_path(clip) + file_name
                trim(file, out_file, section.clip_start, section.clip_end)
                update_tag_and_bag_filename(section.id, gloud_file)
                copy_to_cloud(out_file, gloud_file)
                os.unlink(out_file)

            update_twitch_clip_instance_filename(clip_id, None)
            clip_parts.clear()

        except BaseException as e:
            update_scan_job_error(scan_job_id, str(e))
            cloud_error_logger(e, file=sys.stderr)

            return
        finally:
            if os.path.exists(file):
                os.unlink(file)
        update_scan_job_percent(scan_job_id, 1, True)


def get_clip_path(clip: TwitchClipInstance):
    tmp = clip.created_at
    if isinstance(clip.created_at, str):
        tmp = isoparse(clip.created_at)

    return f'videos/{clip.broadcaster_name}/{str(tmp.year)}/{str(tmp.month)}/{str(tmp.day)}/'


def get_storage_path(clip: TwitchClipInstance):
    storage_path = abspath(get_clip_path(clip))

    if not os.path.exists(storage_path):
        os.makedirs(storage_path)
    return storage_path


def to_hms(seconds: int):
    return time.strftime('%H:%M:%S', time.gmtime(seconds))


def trim(input_path, output_path, start=30, end=60, clip_length=30):
    min_clip = 5 - (end - start)
    if min_clip == 1:
        min_clip = 2
    if min_clip > 0:
        distance_from_end = clip_length - end
        distance_from_start = start
        half_min = min_clip / 2
        if distance_from_start > half_min and distance_from_end > half_min:
            start -= half_min
            end += half_min
        elif distance_from_start > min_clip:
            start -= min_clip
        elif distance_from_end > min_clip:
            end += min_clip

    hms = to_hms(start)
    s = to_hms(end)
    cmd = f'ffmpeg -y -hide_banner -loglevel error -nostdin  -i {input_path} -ss {hms} -to {s} -async 1  {output_path}'
    os.system(cmd)
