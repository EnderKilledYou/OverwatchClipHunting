
import subprocess

from Ocr.clip_to_tag import tag_clipper



def get_length(input_video):
    result = subprocess.run(
        ['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'default=noprint_wrappers=1:nokey=1',
         input_video], stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    return float(result.stdout)


def clip_tag_to_clip(clip_id: int, clip_file: str, scan_job_id: int):
    tag_clipper.add_job((clip_id, clip_file, scan_job_id))

def face_to_clip(clip_id: int, clip_file: str, scan_job_id: int):
    from facer import facer
    facer.add_job((clip_id, clip_file, scan_job_id))
