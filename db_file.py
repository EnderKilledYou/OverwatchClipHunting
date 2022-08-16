import os
from datetime import datetime
from os.path import abspath

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


if __name__ == '__main__':
    write_db_tocloud()
