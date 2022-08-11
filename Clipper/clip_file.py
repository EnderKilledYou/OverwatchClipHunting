class ClipFile:
    file_path: str
    time_start: int
    time_end: int

    def __init__(self, file_path: str, time_start: int, time_end: int):
        self.time_end = time_end
        self.time_start = time_start
        self.file_path = file_path
