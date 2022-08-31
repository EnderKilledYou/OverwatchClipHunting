import cv2
from PIL import Image

from ocr_logic.crop_center import crop
from pipelines.queue_boss import QueueBossBase


class ImagePreprocessor(QueueBossBase):
    def _process(self, image):
        img_grey = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
        thresh = cv2.threshold(img_grey, 0, 255,
                               cv2.THRESH_BINARY_INV | cv2.THRESH_OTSU)[1]
        # edges = cv2.Canny(img_grey, 100, 200)
        pil_grey = Image.fromarray(thresh)
        img_crop = crop(pil_grey)
        img_grey = None
        thresh = None
        edges = None
        pil_grey = None
        return img_crop


ipp = [ImagePreprocessor().start()]


def get_image_pre_processor():
    return ipp[0]
