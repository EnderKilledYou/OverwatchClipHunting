import math
from queue import Queue
from typing import Tuple, Union

import cv2
import numpy as np
from PIL.Image import fromarray

from deskew import determine_skew

from ocr_logic.perma_ocr import PermaOCR, stop_all_ocr, get_perma_ocr


def rotate(
        image: np.ndarray, angle: float, background: Union[int, Tuple[int, int, int]]
) -> np.ndarray:
    old_width, old_height = image.shape[:2]
    angle_radian = math.radians(angle)
    width = abs(np.sin(angle_radian) * old_height) + abs(np.cos(angle_radian) * old_width)
    height = abs(np.sin(angle_radian) * old_width) + abs(np.cos(angle_radian) * old_height)

    image_center = tuple(np.array(image.shape[1::-1]) / 2)
    rot_mat = cv2.getRotationMatrix2D(image_center, angle, 1.0)
    rot_mat[1, 2] += (width - old_width) / 2
    rot_mat[0, 2] += (height - old_height) / 2
    return cv2.warpAffine(image, rot_mat, (int(round(height)), int(round(width))), borderValue=background)


imageread = cv2.imread('sample_images/elim.png')
image = cv2.resize(imageread, None, fx=1.2, fy=1.2, interpolation=cv2.INTER_CUBIC)






grayscale = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

thresh = cv2.threshold(grayscale, 0, 255,
	cv2.THRESH_BINARY_INV | cv2.THRESH_OTSU)[1]
cv2.imshow("Otsu", thresh)



angle = determine_skew(image)
ocr = get_perma_ocr()


edges = cv2.Canny(thresh, 300,400,L2gradient = True)
rotated = rotate(edges, angle, (0, 0, 0))
return_q = Queue()
text = ocr.GetUTF8Text(fromarray(thresh), return_q)
cv2.imshow('img',edges)
print(text)
stop_all_ocr()
cv2.waitKey(0)
cv2.destroyAllWindows()
# cv2.imwrite('output.png', rotated)
