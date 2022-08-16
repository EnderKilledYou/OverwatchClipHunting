from queue import Queue

from Ocr.tag_clipper import TagClipper

tag_clipper = TagClipper()
tag_clipper.start()


def clip_tag_to_clip(clip_id: int, clip_file: str, scan_job_id: int):
    tag_clipper.add_job((clip_id, clip_file, scan_job_id))
