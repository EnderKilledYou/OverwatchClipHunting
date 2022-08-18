import os
from time import sleep

from config.config import tess_fast_dir


def wait_for_tesseract():
    while not os.path.exists(tess_fast_dir + 'eng.traineddata'):
        print("00000000000000000000Waiting for tesseract to install (twitch)...0000000000000000000000000")
        sleep(2)
