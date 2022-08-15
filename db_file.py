import os
from os.path import abspath

os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = abspath("./inspiring-lore-357817-7dede6026287.json")
from google.cloud import storage


def write():
    """Write and read a blob from GCS using file-like IO"""
    # The ID of your GCS bucket
    # bucket_name = "your-bucket-name"

    # The ID of your new GCS object
    # blob_name = "storage-object-name"

    storage_client = storage.Client()
    bucket = storage_client.bucket('app_storage_state')
    blob = bucket.blob("twitch.sqlite3")

    # Mode can be specified as wb/rb for bytes mode.
    # See: https://docs.python.org/3/library/io.html
    with open("twitch.sqlite3", "rb") as db:
        with blob.open("wb") as f:
            f.write(db.read())


def read():
    storage_client = storage.Client()
    bucket = storage_client.bucket('app_storage_state')
    blob = bucket.blob("twitch.sqlite3")
    with blob.open("rb") as f:
        with open("twitch2.sqlite3", "wb") as db:
            db.write()
