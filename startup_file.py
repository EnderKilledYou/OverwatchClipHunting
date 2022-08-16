import os
from os.path import abspath

from google.cloud.storage import Blob

from password import GenerateRandomWindowsPassword

os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = abspath("./inspiring-lore-357817-7dede6026287.json")
from google.cloud import storage


def get_blob_by_path(remote_file) ->Blob:
    storage_client = storage.Client()
    bucket = storage_client.bucket('app_storage_state')

    return bucket.get_blob(remote_file)




def copy_to_cloud(local_file, remote_file):
    storage_client = storage.Client()
    bucket = storage_client.bucket('app_storage_state')
    blob = bucket.blob(remote_file)
    with open(local_file, 'rb') as local:
        local_data = local.read()
        with blob.open('wb') as writer:
            writer.write(local_data)


def read():
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
    if "zombie" not in os.environ:
        read()
    cpuCount = os.cpu_count()
    print("Number of CPUs in the system:", cpuCount)
