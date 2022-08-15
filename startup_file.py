import os
from datetime import datetime
from os.path import abspath

os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = abspath("./inspiring-lore-357817-7dede6026287.json")
from google.cloud import storage


def read():
    storage_client = storage.Client()
    bucket = storage_client.bucket('app_storage_state')
    blob = bucket.blob("twitch.sqlite3")
    with blob.open("rb") as f:
        with open("twitch.sqlite", "wb") as db:
            db.write()

if __name__ == '__main__':
    print("start up file starting")
    read()