
import atexit

import threading
from Database.Twitch.tag_clipper_job import reset_twitch_clip_job_state, requeue_twitch_clip_jobs
from alli import alli
from facer import facer
from google_cloud_helpers.tesseract_install_helper import install
from scanner import rescanner

nothing = ""


def start_workers():
    threading.Thread(target=install, args=[]).start()
    rescanner.start()
    alli.start()
    facer.start()
    reset_twitch_clip_job_state()
    requeue_twitch_clip_jobs(rescanner)
    atexit.register(rescanner.stop)
    atexit.register(alli.stop)
    atexit.register(facer.stop)


threading.Thread(target=start_workers, args=[]).start()
