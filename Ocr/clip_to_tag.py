from Database.Twitch.twitch_clip_instance import TwitchClipInstance
from Ocr.tag_clipper import TagClipper

tag_clipper = TagClipper()
tag_clipper.start()

def clip_tag_to_clip(request, clip: TwitchClipInstance):

    tag_clipper.add_job((request, clip.file_path))
