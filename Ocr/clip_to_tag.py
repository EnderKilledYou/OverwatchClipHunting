from queue import Queue

from Ocr.tag_clipper import TagClipper

tag_clipper = TagClipper()
tag_clipper.start()


def clip_tag_to_clip(clip_id: int, clip_file: str):
    tag_clipper.add_job((clip_id, clip_file))
