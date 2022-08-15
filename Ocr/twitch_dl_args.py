class Args:
    def __init__(self, video_id: str, out_file: str):
        self.quality = "source"
        self.output = out_file
        self.video = video_id
        self.start = None
        self.end = None
        self.overwrite = True
