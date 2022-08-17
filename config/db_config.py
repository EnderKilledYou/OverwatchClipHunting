from flask_sqlalchemy import SQLAlchemy




def config_db() -> SQLAlchemy:
    """

    :rtype: object
    :return: Initializes the sqlite database for storing your credentials.
    """
    from app import app

    dbx = SQLAlchemy(app)
    return dbx


db = config_db()


def init_db():
    from app import app
    #TwitchClipInstanceScanJob()
    from Database.Twitch.twitch_clip_instance_scan_job import TwitchClipInstanceScanJob
    from Database.monitor import get_monitors
    db.init_app(app)
    db.create_all()


def get_db() -> SQLAlchemy:
    return db
