import numpy as np


class Frame:
    """
        Holds the output of VideoCapture and some info
    """

    def __init__(self, frame_number: int, image: np.ndarray, ts_second: int, source_name: str = '', clip_id: int = -1):
        """

        :param frame_number: The Frame Number starting from 0
        :param image: the numpy array of the image
        :param ts_second: the seconds from the start of the capture
        """
        self.frame_number = frame_number
        self.image = image
        self.ts_second = ts_second
        self.source_name = source_name
        self.text = ''
        self.empty = False
        self.clip_id = clip_id

    def __del__(self):
        # print(f"Frame Del")
        if self.image is not None:
            del self.image
        self.image = None
        self.frame_number = None
        self.ts_second = None
        self.source_name = None
        self.text = None
        self.empty = None
        self.clip_id = None

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, tb):
        self.image = None
        return self
