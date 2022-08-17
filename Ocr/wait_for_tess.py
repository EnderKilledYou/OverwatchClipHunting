import os
from time import sleep

from config.config import tess_fast_dir


def wait_for_tess():
    while not os.path.exists(tess_fast_dir):
        print("----------Waiting for tesseract git to clone fi---------------")
        sleep(3)
