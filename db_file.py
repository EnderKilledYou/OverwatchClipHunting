import os
from asyncio import sleep
from datetime import datetime
from os.path import abspath
from threading import Thread

from config.config import tess_fast_dir

os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = abspath("./inspiring-lore-357817-7dede6026287.json")
from google.cloud import storage


def write_db_tocloud():
    storage_client = storage.Client()
    bucket = storage_client.bucket('app_storage_state')
    blob = bucket.blob("twitch.sqlite3")
    time_stamp = bucket.blob("timestamp.txt")

    with open("twitch.sqlite3", "rb") as db:
        data = db.read()
    with blob.open("wb") as f:
        f.write(data)
    with time_stamp.open("w") as t:
        t.write(str(datetime.now()))


def install():
    if not os.path.exists(tess_fast_dir):
        if 'INSTALL_SCRIPT' in os.environ:
            print("--------------Installing Tesseract---------------")
            os.system(os.environ['INSTALL_SCRIPT'])


# threading.Thread(target=install).start()
class RepeatingTimer(Thread):

    def run(self):
        while True:
            sleep(60 * 2)
            print("backing up db")
            write_db_tocloud()
            sleep(60 * 60 * 6)
