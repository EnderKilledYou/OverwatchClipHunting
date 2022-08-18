import atexit

from Database.Twitch.tag_clipper_job import reset_twitch_clip_job_state, requeue_twitch_clip_jobs
from app import app
from heart_beat import alli
from routes.clips import rescanner

nothing = ""


@app.before_first_request
def before_first_request():
    rescanner.start()
    alli.start()
    reset_twitch_clip_job_state()
    requeue_twitch_clip_jobs(rescanner)
    atexit.register(rescanner.stop)
