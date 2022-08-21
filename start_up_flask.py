from app import app
import atexit
import threading
from Database.Twitch.tag_clipper_job import reset_twitch_clip_job_state, requeue_twitch_clip_jobs
from Monitors.heart_beat import HeartBeat
from google_cloud_helpers.tesseract_install_helper import install
from routes.clips import rescanner

nothing = ""
alli = HeartBeat()
startup_lock = threading.Lock()
started = {}


@app.before_first_request
def start_up():
    startup_lock.acquire()
    try:
        if "started" in started:
            return
        threading.Thread(target=install, args=[]).start()
        rescanner.start()
        alli.start()
        reset_twitch_clip_job_state()
        requeue_twitch_clip_jobs(rescanner)
    finally:
        started["started"] = "started"
        startup_lock.release()


atexit.register(rescanner.stop)
atexit.register(alli.stop)
