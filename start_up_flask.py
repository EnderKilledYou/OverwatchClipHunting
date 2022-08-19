import atexit
import threading
from time import sleep

from Database.Twitch.tag_clipper_job import reset_twitch_clip_job_state, requeue_twitch_clip_jobs

from Monitors.heart_beat import HeartBeat
from google_cloud_helpers.tesseract_install_helper import install

from routes.clips import rescanner

nothing = ""
alli = HeartBeat()


def start_up():

    rescanner.start()
    alli.start()
    reset_twitch_clip_job_state()
    requeue_twitch_clip_jobs(rescanner)


atexit.register(rescanner.stop)
atexit.register(alli.stop)

threading.Thread(target=start_up).start()
threading.Thread(target=install, args=[]).start()