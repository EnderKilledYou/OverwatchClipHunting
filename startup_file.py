import os
from os.path import abspath

from google.cloud import storage
from google.cloud.storage import Blob







def copy_to_cloud(local_file, remote_file):
    storage_client = storage.Client()
    bucket = storage_client.bucket('app_storage_state')
    blob = bucket.blob(remote_file)
    with open(local_file, 'rb') as local:
        local_data = local.read()
        with blob.open('wb') as writer:
            writer.write(local_data)


def read_db_from_cloud():
    storage_client = storage.Client()
    bucket = storage_client.bucket('app_storage_state')
    blob = bucket.blob("twitch.sqlite3")
    if not blob.exists(storage_client):
        return
    with blob.open("rb") as f:
        with open("twitch.sqlite", "wb") as db:
            db.write(f.read())


if __name__ == '__main__':
    print("start up file starting")
    count = os.cpu_count()
    print("Cpu threads would be " + str(count))
