import numpy as np


class Frame:
    """
        Holds the output of VideoCapture and some info
    """

    def __init__(self, frame_number: int, image: np.ndarray, ts_second: int, source_name: str = ''):
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
