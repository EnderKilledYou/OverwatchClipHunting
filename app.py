import os
from threading import Thread
from time import sleep

from flask import Flask, jsonify

from config.config import flask_secret_key
from db_file import write_db_tocloud
from startup_file import read_db_from_cloud


def config_app() -> Flask:
    appx = Flask('ocr', static_url_path='',
                 static_folder='templates',
                 template_folder='templates')
    appx.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///twitch.sqlite3'
    appx.config['SECRET_KEY'] = flask_secret_key

    return appx


def register_blueprints(app: Flask):
    from config.db_config import init_db
    init_db()
    from routes.twitch import twitch as twitch_blueprint
    from routes.monitor import monitor as monitor_blueprint
    from routes.clips import clips as clips_blueprint
    from routes.video import video as video_blueprint
    from routes.streamer import streamer as streamer_blueprint

    from routes.zombie import zombie_route as zombie_callback_blueprint

    app.register_blueprint(zombie_callback_blueprint)
    app.register_blueprint(clips_blueprint)
    app.register_blueprint(streamer_blueprint)
    app.register_blueprint(twitch_blueprint)
    app.register_blueprint(monitor_blueprint)
    app.register_blueprint(video_blueprint)


app = config_app()
app.url_map.strict_slashes = False
register_blueprints(app)


class RepeatingTimer(Thread):

    def run(self):
        while True:
            sleep(60 * 2)
            print("backing up db")
            write_db_tocloud()
            sleep(60 * 60 * 6)


@app.route("/heartbeat")
def heartbeat():
    return jsonify({"status": "healthy"})


@app.errorhandler(404)
def not_found(e):
    return app.send_static_file("index.html")

if 'OCR_PRODUCTION' in os.environ:
    read_db_from_cloud()
    thread = RepeatingTimer()
    thread.start()
if __name__ == '__main__':
    app.run(threaded=True)
