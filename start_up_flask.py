import atexit
import threading

from Database.Twitch.tag_clipper_job import reset_twitch_clip_job_state, requeue_twitch_clip_jobs
from app import app
from Monitors.heart_beat import HeartBeat
from config.db_config import init_db
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

threading.Thread(target=start_up)
