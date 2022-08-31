from queue import Queue

from ocr_logic.perma_ocr import get_perma_ocr
from pipelines.queue_boss import QueueBossBase


class Image2Textprocessor(QueueBossBase):
    def _process(self, cropped_image):
        return_queue = Queue()
        api = get_perma_ocr()
        text = api.GetUTF8Text(cropped_image, return_queue)
        cropped_image = None
        return_queue = None
        img_crop = None
        return text


i2t = [Image2Textprocessor().start()]


def get_image_to_text_processor():
    return i2t[0]
