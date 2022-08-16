from pytesseract import image_to_string

from Clipper.get_unix_time import get_unix_time


def test_reg():

    start = get_unix_time()
    image_to_string('img.png')
    end = get_unix_time()
    diff = end - start
    print(diff)
    return diff


def test_fast():
    start = get_unix_time()
    image_to_string('img.png',config=r'--tessdata-dir "C:\\tmp\\tessdata_fast"',lang='eng')
    end = get_unix_time()
    diff = end - start
    print(diff)
    return diff


if __name__ == '__main__':
    test_reg()