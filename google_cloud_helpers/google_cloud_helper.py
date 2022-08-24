import os

from os.path import abspath

from google.cloud import storage
from google.cloud.storage import Blob

os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = abspath("./inspiring-lore-357817-7dede6026287.json")


def get_blob_by_path(remote_file) -> Blob:
    storage_client = storage.Client()
    bucket = storage_client.bucket('app_storage_state')
    return bucket.get_blob(remote_file)
