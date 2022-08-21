from app import app
import atexit
import threading
from Database.Twitch.tag_clipper_job import reset_twitch_clip_job_state, requeue_twitch_clip_jobs
from Monitors.heart_beat import HeartBeat
from google_cloud_helpers.tesseract_install_helper import install
from routes.clips import rescanner

nothing = ""
alli = HeartBeat()


def start_workers():
    threading.Thread(target=install, args=[]).start()
    rescanner.start()
    alli.start()
    reset_twitch_clip_job_state()
    requeue_twitch_clip_jobs(rescanner)
    atexit.register(rescanner.stop)
    atexit.register(alli.stop)


threading.Thread(target=start_workers, args=[]).start()
