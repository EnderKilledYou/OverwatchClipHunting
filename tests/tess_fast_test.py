from pytesseract import image_to_string
from tesserocr import PyTessBaseAPI

from generic_helpers.get_unix_time import get_unix_time


def test_reg():

    start = get_unix_time()
    for i in range(0, 100):
        image_to_string('../image_flask.png')
    end = get_unix_time()
    diff = end - start
    print(diff)
    return diff


def test_fast():
    start = get_unix_time()
    for i in range(0,100):
        image_to_string('../image_flask.png',config=r'--tessdata-dir "C:\\tmp\\tessdata_fast"',lang='eng')
    end = get_unix_time()
    diff = end - start
    print(diff)
    return diff

def test_tesserocr():
    start = get_unix_time()
    with PyTessBaseAPI(path="C:\\tmp\\tessdata_fast") as api:
        for i in range(0, 100):

            api.SetImageFile('../image_flask.png')
            print(api.GetUTF8Text())

    end = get_unix_time()
    diff = end - start
    print(diff)
    return diff

if __name__ == '__main__':
    test_reg()